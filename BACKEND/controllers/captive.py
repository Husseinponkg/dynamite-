"""Public captive-portal flows: list packages, pay, redeem voucher."""
from datetime import datetime, timedelta
from config.db import connection
from services.azampay import initiate_azampay_payment, _provider_for_method


class Captive:
    def __init__(self, data=None):
        self.data = data

    async def public_packages(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, package_name, package_desc, price, validity_days, validity_hours,
                           bandwidth_up, bandwidth_down, data_limit, concurrent_logins
                    FROM package WHERE status = 'active'
                    ORDER BY price ASC
                    """
                )
                rows = await cur.fetchall()
            packages = [
                {
                    "id": r[0],
                    "package_name": r[1],
                    "package_desc": r[2],
                    "price": float(r[3]) if r[3] else 0,
                    "validity_days": r[4],
                    "validity_hours": r[5],
                    "bandwidth_up": r[6],
                    "bandwidth_down": r[7],
                    "data_limit": r[8],
                    "concurrent_logins": r[9],
                }
                for r in rows
            ]
            return {"success": True, "packages": packages}
        finally:
            if conn:
                await conn.close()

    async def checkout(self):
        """Initiate mobile money payment from captive portal (no login required)."""
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT id, package_name, price FROM package WHERE id = %s AND status = 'active'",
                    (self.data.package_id,),
                )
                pkg = await cur.fetchone()
                if not pkg:
                    return {"success": False, "message": "Package not found"}

            amount = float(pkg[2])
            ref = f"CAP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{self.data.package_id}"
            method = self.data.payment_method.lower()

            # Cash / offline
            if method == "cash":
                conn2 = await connection()
                try:
                    async with conn2.cursor() as cur:
                        await cur.execute(
                            """
                            INSERT INTO payments (
                                user_id, package_id, router_id, amount, payment_method,
                                transaction_id, phone_number, reference_number, status, notes
                            ) VALUES (
                                NULL, %s, %s, %s, 'cash', %s, %s, %s, 'completed', %s
                            )
                            RETURNING id, reference_number, status, amount
                            """,
                            (
                                self.data.package_id,
                                self.data.router_id,
                                amount,
                                ref,
                                self.data.phone_number,
                                ref,
                                f"MAC:{self.data.mac_address or 'n/a'}",
                            ),
                        )
                        row = await cur.fetchone()
                        await conn2.commit()
                    return {
                        "success": True,
                        "message": "Cash payment recorded. Connect using voucher or ask admin.",
                        "payment": {
                            "id": row[0],
                            "reference_number": row[1],
                            "status": row[2],
                            "amount": float(row[3]),
                        },
                    }
                finally:
                    await conn2.close()

            # Mobile money via AzamPay
            try:
                provider = _provider_for_method(method)
            except Exception:
                provider = method.upper()

            gateway = await initiate_azampay_payment(
                amount=amount,
                phone_number=self.data.phone_number,
                external_id=ref,
                provider=provider,
            )

            conn2 = await connection()
            try:
                status = "pending" if gateway.get("success") else "failed"
                tx_id = gateway.get("transaction_id", ref)
                async with conn2.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO payments (
                            user_id, package_id, router_id, amount, payment_method,
                            transaction_id, phone_number, reference_number, status, notes
                        ) VALUES (
                            NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        RETURNING id, reference_number, status, amount
                        """,
                        (
                            self.data.package_id,
                            self.data.router_id,
                            amount,
                            method,
                            tx_id,
                            self.data.phone_number,
                            ref,
                            status,
                            f"captive MAC:{self.data.mac_address or 'n/a'}",
                        ),
                    )
                    row = await cur.fetchone()
                    await conn2.commit()
                return {
                    "success": bool(gateway.get("success")),
                    "message": "USSD push sent — approve on your phone" if gateway.get("success") else gateway.get("message", "Payment failed"),
                    "payment": {
                        "id": row[0],
                        "reference_number": row[1],
                        "status": row[2],
                        "amount": float(row[3]),
                    },
                    "package_name": pkg[1],
                }
            finally:
                await conn2.close()
        except Exception as e:
            if conn:
                await conn.close()
            return {"success": False, "message": str(e)}

    async def redeem(self):
        """Redeem voucher from captive portal and optionally open a session."""
        from controllers.vouchers import Vouchers
        from models.vouchers import RedeemVoucher

        result = await Vouchers(
            RedeemVoucher(
                voucher_code=self.data.voucher_code,
                phone=self.data.phone,
                mac_address=self.data.mac_address,
            )
        ).redeem()

        if not result.get("success"):
            return result

        # Create session record for tracking
        try:
            conn = await connection()
            session_id = f"v-{self.data.voucher_code}-{datetime.utcnow().timestamp():.0f}"
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO active_sessions (
                        user_id, router_id, session_id, mac_address, status
                    ) VALUES (NULL, %s, %s, %s, 'active')
                    ON CONFLICT (session_id) DO NOTHING
                    """,
                    (result.get("router_id"), session_id, self.data.mac_address),
                )
                await conn.commit()
            await conn.close()
            result["session_id"] = session_id
        except Exception:
            pass

        return result
