import secrets
import string
from datetime import datetime, timedelta
from config.db import connection
from models.vouchers import GenerateVouchers, RedeemVoucher, UpdateVoucherStatus


class Vouchers:
    def __init__(self, data=None):
        self.data = data

    def _generate_code(self, prefix: str, length: int) -> str:
        alphabet = string.ascii_uppercase + string.digits
        random_part = "".join(secrets.choice(alphabet) for _ in range(length))
        return f"{prefix}-{random_part}"

    def _format_voucher(self, row) -> dict:
        if not row:
            return None
        return {
            "id": row[0],
            "voucher_code": row[1],
            "package_id": row[2],
            "router_id": row[3],
            "created_by": row[4],
            "used_by": row[5],
            "status": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
            "expire_at": row[8].isoformat() if row[8] else None,
            "used_at": row[9].isoformat() if row[9] else None,
            "package_name": row[10] if len(row) > 10 else None,
            "router_name": row[11] if len(row) > 11 else None,
            "price": float(row[12]) if len(row) > 12 and row[12] is not None else None,
        }

    async def generate(self):
        conn = None
        try:
            conn = await connection()
            codes = []
            expire_at = datetime.utcnow() + timedelta(days=self.data.expire_days)
            created = []

            async with conn.cursor() as cursor:
                # Validate package & router exist
                await cursor.execute(
                    "SELECT id, package_name, price FROM package WHERE id = %s AND status = 'active'",
                    (self.data.package_id,),
                )
                pkg = await cursor.fetchone()
                if not pkg:
                    return {"success": False, "message": "Package not found or inactive"}

                await cursor.execute(
                    "SELECT id, router_name FROM routers WHERE id = %s",
                    (self.data.router_id,),
                )
                rtr = await cursor.fetchone()
                if not rtr:
                    return {"success": False, "message": "Router not found"}

                for _ in range(self.data.quantity):
                    for attempt in range(10):
                        code = self._generate_code(self.data.prefix, self.data.code_length)
                        await cursor.execute(
                            "SELECT id FROM vouchers WHERE voucher_code = %s", (code,)
                        )
                        if not await cursor.fetchone():
                            break
                    else:
                        continue

                    await cursor.execute(
                        """
                        INSERT INTO vouchers (
                            voucher_code, package_id, router_id, created_by,
                            status, expire_at
                        ) VALUES (%s, %s, %s, %s, 'active', %s)
                        RETURNING id, voucher_code, package_id, router_id, created_by,
                                  used_by, status, created_at, expire_at, used_at
                        """,
                        (
                            code,
                            self.data.package_id,
                            self.data.router_id,
                            self.data.created_by,
                            expire_at,
                        ),
                    )
                    row = await cursor.fetchone()
                    created.append(
                        {
                            "id": row[0],
                            "voucher_code": row[1],
                            "package_id": row[2],
                            "router_id": row[3],
                            "status": row[6],
                            "created_at": row[7].isoformat() if row[7] else None,
                            "expire_at": row[8].isoformat() if row[8] else None,
                            "package_name": pkg[1],
                            "router_name": rtr[1],
                            "price": float(pkg[2]) if pkg[2] else 0,
                        }
                    )

            await conn.commit()
            return {
                "success": True,
                "message": f"Generated {len(created)} voucher(s)",
                "count": len(created),
                "vouchers": created,
            }
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def get_all(self, status: str = None, package_id: int = None, router_id: int = None, search: str = None, limit: int = 100, offset: int = 0):
        conn = None
        try:
            conn = await connection()
            conditions = ["1=1"]
            params = []

            if status:
                conditions.append("v.status = %s")
                params.append(status)
            if package_id:
                conditions.append("v.package_id = %s")
                params.append(package_id)
            if router_id:
                conditions.append("v.router_id = %s")
                params.append(router_id)
            if search:
                conditions.append("v.voucher_code ILIKE %s")
                params.append(f"%{search}%")

            where = " AND ".join(conditions)
            params.extend([limit, offset])

            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"""
                    SELECT v.id, v.voucher_code, v.package_id, v.router_id, v.created_by,
                           v.used_by, v.status, v.created_at, v.expire_at, v.used_at,
                           p.package_name, r.router_name, p.price
                    FROM vouchers v
                    LEFT JOIN package p ON p.id = v.package_id
                    LEFT JOIN routers r ON r.id = v.router_id
                    WHERE {where}
                    ORDER BY v.created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = await cursor.fetchall()

                count_params = params[:-2] if len(params) >= 2 else list(params)
                await cursor.execute(
                    f"SELECT COUNT(*) FROM vouchers v WHERE {where}",
                    count_params,
                )
                total = (await cursor.fetchone())[0]

            return {
                "success": True,
                "total": total,
                "vouchers": [self._format_voucher(r) for r in rows],
            }
        except Exception as e:
            raise e
        finally:
            if conn:
                await conn.close()

    async def get_one(self, voucher_id: int = None, code: str = None):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cursor:
                if code:
                    await cursor.execute(
                        """
                        SELECT v.id, v.voucher_code, v.package_id, v.router_id, v.created_by,
                               v.used_by, v.status, v.created_at, v.expire_at, v.used_at,
                               p.package_name, r.router_name, p.price
                        FROM vouchers v
                        LEFT JOIN package p ON p.id = v.package_id
                        LEFT JOIN routers r ON r.id = v.router_id
                        WHERE v.voucher_code = %s
                        """,
                        (code.upper().strip(),),
                    )
                else:
                    await cursor.execute(
                        """
                        SELECT v.id, v.voucher_code, v.package_id, v.router_id, v.created_by,
                               v.used_by, v.status, v.created_at, v.expire_at, v.used_at,
                               p.package_name, r.router_name, p.price
                        FROM vouchers v
                        LEFT JOIN package p ON p.id = v.package_id
                        LEFT JOIN routers r ON r.id = v.router_id
                        WHERE v.id = %s
                        """,
                        (voucher_id,),
                    )
                row = await cursor.fetchone()
            if not row:
                return {"success": False, "message": "Voucher not found"}
            return {"success": True, "voucher": self._format_voucher(row)}
        finally:
            if conn:
                await conn.close()

    async def redeem(self):
        conn = None
        try:
            conn = await connection()
            code = self.data.voucher_code.upper().strip()
            now = datetime.utcnow()

            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT v.id, v.voucher_code, v.package_id, v.router_id, v.status,
                           v.expire_at, p.package_name, p.validity_days, p.validity_hours,
                           p.bandwidth_up, p.bandwidth_down, p.data_limit, p.price
                    FROM vouchers v
                    JOIN package p ON p.id = v.package_id
                    WHERE v.voucher_code = %s
                    FOR UPDATE
                    """,
                    (code,),
                )
                row = await cursor.fetchone()
                if not row:
                    return {"success": False, "message": "Invalid voucher code"}

                vid, vcode, pkg_id, rtr_id, status, expire_at = row[0], row[1], row[2], row[3], row[4], row[5]
                if status != "active":
                    return {"success": False, "message": f"Voucher is {status}"}
                if expire_at and expire_at < now:
                    await cursor.execute(
                        "UPDATE vouchers SET status = 'expired' WHERE id = %s", (vid,)
                    )
                    await conn.commit()
                    return {"success": False, "message": "Voucher has expired"}

                await cursor.execute(
                    """
                    UPDATE vouchers
                    SET status = 'used', used_by = %s, used_at = %s
                    WHERE id = %s
                    """,
                    (self.data.user_id, now, vid),
                )

                # Record package history if user_id present
                if self.data.user_id:
                    validity = timedelta(days=row[7] or 0, hours=row[8] or 0)
                    expires = now + validity
                    await cursor.execute(
                        """
                        INSERT INTO package_history (user_id, package_id, router_id, expires_at)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (self.data.user_id, pkg_id, rtr_id, expires),
                    )

            await conn.commit()
            return {
                "success": True,
                "message": "Voucher redeemed successfully",
                "package": {
                    "id": pkg_id,
                    "name": row[6],
                    "validity_days": row[7],
                    "validity_hours": row[8],
                    "bandwidth_up": row[9],
                    "bandwidth_down": row[10],
                    "data_limit": row[11],
                    "price": float(row[12]) if row[12] else 0,
                },
                "router_id": rtr_id,
            }
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def cancel(self, voucher_id: int):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE vouchers SET status = 'cancelled'
                    WHERE id = %s AND status = 'active'
                    RETURNING id, voucher_code, status
                    """,
                    (voucher_id,),
                )
                row = await cursor.fetchone()
                await conn.commit()
            if not row:
                return {"success": False, "message": "Voucher not found or not active"}
            return {"success": True, "message": "Voucher cancelled", "id": row[0], "code": row[1]}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def stats(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE status = 'active') as active,
                        COUNT(*) FILTER (WHERE status = 'used') as used,
                        COUNT(*) FILTER (WHERE status = 'expired') as expired,
                        COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled,
                        COUNT(*) as total
                    FROM vouchers
                    """
                )
                row = await cursor.fetchone()
            return {
                "success": True,
                "stats": {
                    "active": row[0] or 0,
                    "used": row[1] or 0,
                    "expired": row[2] or 0,
                    "cancelled": row[3] or 0,
                    "total": row[4] or 0,
                },
            }
        finally:
            if conn:
                await conn.close()
