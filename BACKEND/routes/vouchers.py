from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.vouchers import GenerateVouchers, RedeemVoucher
from controllers.vouchers import Vouchers

router = APIRouter(tags=["Vouchers"])


@router.post("/generate")
async def generate_vouchers(data: GenerateVouchers):
    result = await Vouchers(data).generate()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed"))
    return result


@router.get("/")
async def list_vouchers(
    status: Optional[str] = None,
    package_id: Optional[int] = None,
    router_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await Vouchers().get_all(status, package_id, router_id, search, limit, offset)


@router.get("/stats")
async def voucher_stats():
    return await Vouchers().stats()


@router.get("/code/{code}")
async def get_by_code(code: str):
    result = await Vouchers().get_one(code=code)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.get("/{voucher_id}")
async def get_voucher(voucher_id: int):
    result = await Vouchers().get_one(voucher_id=voucher_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.post("/redeem")
async def redeem_voucher(data: RedeemVoucher):
    result = await Vouchers(data).redeem()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/{voucher_id}/cancel")
async def cancel_voucher(voucher_id: int):
    result = await Vouchers().cancel(voucher_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
