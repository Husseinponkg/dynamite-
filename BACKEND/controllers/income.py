from config.db import connection


class Income:
    async def summary(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                # Payments income (completed only)
                await cur.execute(
                    """
                    SELECT
                        COALESCE(SUM(amount) FILTER (WHERE status ILIKE 'completed' AND created_at::date = CURRENT_DATE), 0),
                        COALESCE(SUM(amount) FILTER (WHERE status ILIKE 'completed' AND created_at >= date_trunc('week', CURRENT_DATE)), 0),
                        COALESCE(SUM(amount) FILTER (WHERE status ILIKE 'completed' AND created_at >= date_trunc('month', CURRENT_DATE)), 0),
                        COALESCE(SUM(amount) FILTER (WHERE status ILIKE 'completed'), 0),
                        COUNT(*) FILTER (WHERE status ILIKE 'completed'),
                        COUNT(*) FILTER (WHERE status ILIKE 'pending'),
                        COUNT(*) FILTER (WHERE status ILIKE 'failed')
                    FROM payments
                    """
                )
                p = await cur.fetchone()

                # Voucher value redeemed (used vouchers * package price)
                await cur.execute(
                    """
                    SELECT COALESCE(SUM(p.price), 0)
                    FROM vouchers v
                    JOIN package p ON p.id = v.package_id
                    WHERE v.status = 'used'
                    """
                )
                voucher_revenue = (await cur.fetchone())[0] or 0

                # Withdraws completed
                await cur.execute(
                    """
                    SELECT COALESCE(SUM(amount) FILTER (WHERE status = 'completed'), 0),
                           COALESCE(SUM(amount) FILTER (WHERE status = 'pending'), 0)
                    FROM withdraws
                    """
                )
                try:
                    w = await cur.fetchone()
                except Exception:
                    w = (0, 0)

                # By payment method
                await cur.execute(
                    """
                    SELECT payment_method,
                           COUNT(*) as cnt,
                           COALESCE(SUM(amount), 0) as total
                    FROM payments
                    WHERE status ILIKE 'completed'
                    GROUP BY payment_method
                    ORDER BY total DESC
                    """
                )
                methods = [
                    {"method": r[0], "count": r[1], "total": float(r[2])}
                    for r in await cur.fetchall()
                ]

                # Recent completed payments
                await cur.execute(
                    """
                    SELECT id, amount, payment_method, phone_number, reference_number,
                           status, created_at, transaction_id
                    FROM payments
                    ORDER BY created_at DESC
                    LIMIT 20
                    """
                )
                recent = []
                for r in await cur.fetchall():
                    recent.append({
                        "id": r[0],
                        "amount": float(r[1]) if r[1] else 0,
                        "payment_method": r[2],
                        "phone_number": r[3],
                        "reference_number": r[4],
                        "status": r[5],
                        "created_at": r[6].isoformat() if r[6] else None,
                        "transaction_id": r[7],
                    })

            total_income = float(p[3] or 0) + float(voucher_revenue)
            withdrawn = float(w[0] or 0)
            pending_withdraw = float(w[1] or 0)
            available = total_income - withdrawn - pending_withdraw

            return {
                "success": True,
                "income": {
                    "today": float(p[0] or 0),
                    "this_week": float(p[1] or 0),
                    "this_month": float(p[2] or 0),
                    "all_time_payments": float(p[3] or 0),
                    "voucher_revenue": float(voucher_revenue),
                    "total_income": total_income,
                    "withdrawn": withdrawn,
                    "pending_withdraw": pending_withdraw,
                    "available_balance": max(available, 0),
                },
                "payment_counts": {
                    "completed": p[4] or 0,
                    "pending": p[5] or 0,
                    "failed": p[6] or 0,
                },
                "by_method": methods,
                "recent_transactions": recent,
            }
        finally:
            if conn:
                await conn.close()

    async def list_payments(self, status: str = None, limit: int = 100, offset: int = 0):
        conn = None
        try:
            conn = await connection()
            conditions = ["1=1"]
            params = []
            if status:
                conditions.append("status ILIKE %s")
                params.append(status)
            where = " AND ".join(conditions)
            params.extend([limit, offset])
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT id, user_id, package_id, router_id, amount, payment_method,
                           transaction_id, phone_number, reference_number, status,
                           created_at, completed_at, notes
                    FROM payments
                    WHERE {where}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = await cur.fetchall()
            payments = []
            for r in rows:
                payments.append({
                    "id": r[0],
                    "user_id": r[1],
                    "package_id": r[2],
                    "router_id": r[3],
                    "amount": float(r[4]) if r[4] else 0,
                    "payment_method": r[5],
                    "transaction_id": r[6],
                    "phone_number": r[7],
                    "reference_number": r[8],
                    "status": r[9],
                    "created_at": r[10].isoformat() if r[10] else None,
                    "completed_at": r[11].isoformat() if r[11] else None,
                    "notes": r[12],
                })
            return {"success": True, "payments": payments}
        finally:
            if conn:
                await conn.close()
