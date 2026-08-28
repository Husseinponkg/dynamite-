from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from models.payments import InitiatePay, AzamPayCallback, PaymentStatus
from controllers.payments import Payments

router = APIRouter(prefix="/payments", tags=["Payments Lifecycle Core"])

@router.post("/initiate", status_code=status.HTTP_201_CREATED)
async def checkout_initiate(payload: InitiatePay):
    engine = Payments(data=payload)
    result = await engine.initiate_payment()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message", "Gateway rejected checkout."))
    return result

@router.post("/callback", status_code=status.HTTP_200_OK)
async def azampay_webhook_receiver(payload: AzamPayCallback):
    engine = Payments()
    result = await engine.azam_callback(payload)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return {"message": "Callback acknowledged successfully"}

@router.get("/status/{reference_number}")
async def fetch_transaction_state(reference_number: str):
    engine = Payments()
    result = await engine.get_status(PaymentStatus(reference_number=reference_number))
    return result
