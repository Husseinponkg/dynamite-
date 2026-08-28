from models.payments import InitiatePay, PaymentCallback, PaymentUpdate
from services.azampay import check_azampay_payment_status, initiate_azampay_payment, _provider_for_method
from config.db import connection
from datetime import datetime, timedelta

class Payments:
    def __init__(self, pay: InitiatePay = None, data: InitiatePay = None):
        self.pay = pay or data
        self.data = self.pay

    async def Initiate_pay(self):
        conn = None
        try:
            # 1. Map payment operator network
            provider = _provider_for_method(self.pay.payment_method)
            
            # 2. Trigger USSD push via integration layer
            gateway_response = await initiate_azampay_payment(
                amount=self.pay.amount,
                phone_number=self.pay.phone_number,
                external_id=self.pay.reference_number,
                provider=provider
            )
            
            now = datetime.now()
            expiry = now + timedelta(minutes=15)
            azampay_id = gateway_response.get("transaction_id", self.pay.reference_number)
            initial_status = "PENDING" if gateway_response["success"] else "FAILED"

            conn = await connection()
            async with conn.cursor() as cursor:
                query = """
                    INSERT INTO payments (
                        amount, payment_method, transaction_id, phone_number,
                        reference_number, status, created_at, updated_at,
                        completed_at, expiry_date, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, amount, payment_method, transaction_id, 
                              phone_number, reference_number, status, created_at
                """
                values = (
                    self.pay.amount, self.pay.payment_method, azampay_id, self.pay.phone_number,
                    self.pay.reference_number, initial_status, now, now, None, expiry, self.pay.notes
                )
                await cursor.execute(query, values)
                record = await cursor.fetchone()
                await conn.commit()

            return {
                "success": gateway_response["success"],
                "message": "Payment processing initiated" if gateway_response["success"] else "External provider failed",
                "payment": {
                    "id": record[0],
                    "amount": float(record[1]),
                    "payment_method": record[2],
                    "transaction_id": record[3],
                    "phone_number": record[4],
                    "reference_number": record[5],
                    "status": record[6],
                    "created_at": record[7]
                }
            }
        except Exception as e:
            if conn: await conn.rollback()
            raise e
        finally:
            if conn: await conn.close()

    async def handle_callback(self, callback_data: PaymentCallback):
        """Processes the asynchronous webhook validation ping from AzamPay."""
        conn = None
        try:
            conn = await connection()
            now = datetime.now()
            
            # Map AzamPay webhook response flags to systemic status records
            final_status = "COMPLETED" if callback_data.status.upper() == "SUCCESS" else "FAILED"
            
            async with conn.cursor() as cursor:
                query = """
                    UPDATE payments 
                    SET status = %s, updated_at = %s, completed_at = %s 
                    WHERE transaction_id = %s OR reference_number = %s
                    RETURNING id, reference_number, status
                """
                await cursor.execute(query, (final_status, now, now, callback_data.id, callback_data.reference))
                updated_record = await cursor.fetchone()
                await conn.commit()
                
            if updated_record:
                return {"success": True, "reference": updated_record[1], "status": updated_record[2]}
            return {"success": False, "message": "Transaction record matching callback not found"}
        except Exception as e:
            if conn: await conn.rollback()
            raise e
        finally:
            if conn: await conn.close()

    async def check_status(self, reference_number: str):
        """Queries local database status, or syncs status directly from backend API."""
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cursor:
                query = "SELECT transaction_id, status, amount FROM payments WHERE reference_number = %s"
                await cursor.execute(query, (reference_number,))
                record = await cursor.fetchone()

            if not record:
                return {"message": "Transaction not found"}

            tx_id, current_status, amount = record[0], record[1], record[2]

            # Re-verify against live system context if it was hanging in a pending state
            if current_status == "PENDING":
                live_status = await check_azampay_payment_status(tx_id)
                if live_status in ["SUCCESS", "COMPLETED"]:
                    current_status = "COMPLETED"
                    # Run DB Update code block dynamically or let callback catch it
            
            return {"reference_number": reference_number, "status": current_status, "amount": float(amount)}
        finally:
            if conn: await conn.close()


    async def initiate_payment(self):
        return await self.Initiate_pay()

    async def azam_callback(self, payload):
        return await self.handle_callback(payload)

    async def get_status(self, status_obj):
        ref = status_obj.reference_number if hasattr(status_obj, "reference_number") else status_obj
        return await self.check_status(ref)
