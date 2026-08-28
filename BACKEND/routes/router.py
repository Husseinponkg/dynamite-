from fastapi import APIRouter

from models.routmodels import createrouting,statusview

from controllers.routers import Routers


router = APIRouter()


@router.post("/create-router")
async def routerCreate(
    api: createrouting
):

    route = Routers(api)

    return await route.createRouter()

@router.post("/status")
async def getstatus(data: statusview):
    route = Routers(data)
    return await route.view_status(data.router_id)