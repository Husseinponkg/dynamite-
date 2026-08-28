from datetime import datetime
from config.db import connection
from controllers.income import Income


class Withdraws:
    def __init__(self, data=None):
        self.data = data

    def _fmt(self, row):
        if not row:
            return None
        return {
            "id": row[0],
            "admin_id": row[1],
            "amount": float(row[2]) if row[2] else 0,
            "method": row[3],
            "account_number": row[4],
            "account_name": row[5],
            "status": row[6],
            "notes": row[7],
            "processed_by": row[8],
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None,
            "completed_at": row[11].isoformat() if row[11] else None,
        }

    async def create(self):
        conn = None
        try:
            # Check available balance
            summary = await Income().summary()
            available = summary["income"]["available_balance"]
            amount = float(self.data.amount)
            if amount > available:
                return {
                    "success": False,
                    "message": f"Insufficient balance. Available: TZS {available:,.0f}",
                }

            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO withdraws (
                        admin_id, amount, method, account_number, account_name, status, notes
                    ) VALUES (%s, %s, %s, %s, %s, 'pending', %s)
                    RETURNING id, admin_id, amount, method, account_number, account_name,
                              status, notes, processed_by, created_at, updated_at, completed_at
                    """,
                    (
                        self.data.admin_id,
                        amount,
                        self.data.method.value if hasattr(self.data.method, "value") else self.data.method,
                        self.data.account_number,
                        self.data.account_name,
                        self.data.notes,
                    ),
                )
                row = await cur.fetchone()
                await conn.commit()
            return {"success": True, "message": "Withdraw request submitted", "withdraw": self._fmt(row)}
        except Exception as e:
            if conn:
                await conn.rollback()
            # Table might not exist
            msg = str(e)
            if "withdraws" in msg.lower() and "does not exist" in msg.lower():
                return {"success": False, "message": "Run migrate_add_billing_tables.sql first"}
            raise e
        finally:
            if conn:
                await conn.close()

    async def list_all(self, status: str = None, limit: int = 50):
        conn = None
        try:
            conn = await connection()
            conditions = ["1=1"]
            params = []
            if status:
                conditions.append("status = %s")
                params.append(status)
            where = " AND ".join(conditions)
            params.append(limit)
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT id, admin_id, amount, method, account_number, account_name,
                           status, notes, processed_by, created_at, updated_at, completed_at
                    FROM withdraws
                    WHERE {where}
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    params,
                )
                rows = await cur.fetchall()
            return {"success": True, "withdraws": [self._fmt(r) for r in rows]}
        except Exception as e:
            if "does not exist" in str(e).lower():
                return {"success": True, "withdraws": [], "message": "withdraws table missing — run migration"}
            raise e
        finally:
            if conn:
                await conn.close()

    async def update_status(self, withdraw_id: int, status: str, notes: str = None, processed_by: int = None):
        conn = None
        try:
            conn = await connection()
            now = datetime.utcnow()
            completed = now if status == "completed" else None
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE withdraws SET
                        status = %s,
                        notes = COALESCE(%s, notes),
                        processed_by = COALESCE(%s, processed_by),
                        updated_at = %s,
                        completed_at = COALESCE(%s, completed_at)
                    WHERE id = %s
                    RETURNING id, admin_id, amount, method, account_number, account_name,
                              status, notes, processed_by, created_at, updated_at, completed_at
                    """,
                    (status, notes, processed_by, now, completed, withdraw_id),
                )
                row = await cur.fetchone()
                await conn.commit()
            if not row:
                return {"success": False, "message": "Withdraw not found"}
            return {"success": True, "withdraw": self._fmt(row)}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()
