from fastapi import APIRouter, HTTPException
from models.captive import CaptiveCheckout, CaptiveRedeem
from controllers.captive import Captive

router = APIRouter(tags=["Captive Portal"])


@router.get("/packages")
async def public_packages():
    """Public endpoint — WiFi users see available packages without login."""
    return await Captive().public_packages()


@router.post("/checkout")
async def captive_checkout(data: CaptiveCheckout):
    result = await Captive(data).checkout()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/redeem")
async def captive_redeem(data: CaptiveRedeem):
    result = await Captive(data).redeem()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
