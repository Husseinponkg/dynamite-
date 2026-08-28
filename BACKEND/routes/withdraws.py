from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.withdraws import CreateWithdraw, UpdateWithdraw
from controllers.withdraws import Withdraws

router = APIRouter(tags=["Withdraws"])


@router.post("/")
async def request_withdraw(data: CreateWithdraw):
    result = await Withdraws(data).create()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/")
async def list_withdraws(status: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    return await Withdraws().list_all(status, limit)


@router.patch("/{withdraw_id}")
async def update_withdraw(withdraw_id: int, data: UpdateWithdraw):
    result = await Withdraws().update_status(
        withdraw_id,
        data.status.value if hasattr(data.status, "value") else data.status,
        data.notes,
        data.processed_by,
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result
