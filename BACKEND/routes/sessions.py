from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.sessions import CreateSession, EndSession
from controllers.sessions import Sessions

router = APIRouter(tags=["Sessions"])


@router.get("/")
async def list_sessions(
    status: Optional[str] = "active",
    router_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
):
    return await Sessions().list_sessions(status, router_id, limit)


@router.get("/stats")
async def session_stats():
    return await Sessions().stats()


@router.post("/")
async def create_session(data: CreateSession):
    return await Sessions(data).create()


@router.post("/end")
async def end_session(data: EndSession):
    result = await Sessions().end(data.session_id, data.bandwidth_up_used or 0, data.bandwidth_down_used or 0)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result
