from fastapi import APIRouter, Query
from typing import Optional
from controllers.income import Income

router = APIRouter(tags=["Income"])


@router.get("/summary")
async def income_summary():
    return await Income().summary()


@router.get("/payments")
async def list_payments(
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await Income().list_payments(status, limit, offset)
