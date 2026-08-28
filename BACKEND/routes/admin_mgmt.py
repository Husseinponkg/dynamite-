from fastapi import APIRouter, HTTPException, Query
from models.admin_mgmt import CreateAdmin, UpdateAdmin, CreateBranch
from controllers.admin_mgmt import AdminMgmt

router = APIRouter(tags=["Admin Management"])


@router.get("/admins")
async def list_admins():
    return await AdminMgmt().list_admins()


@router.post("/admins")
async def create_admin(data: CreateAdmin):
    result = await AdminMgmt(data).create_admin()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.put("/admins/{admin_id}")
async def update_admin(admin_id: int, data: UpdateAdmin):
    result = await AdminMgmt(data).update_admin(admin_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.delete("/admins/{admin_id}")
async def delete_admin(admin_id: int):
    result = await AdminMgmt().delete_admin(admin_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result


@router.get("/users")
async def list_users(limit: int = Query(100, ge=1, le=500)):
    return await AdminMgmt().list_users(limit)


@router.get("/branches")
async def list_branches():
    return await AdminMgmt().list_branches()


@router.post("/branches")
async def create_branch(data: CreateBranch):
    result = await AdminMgmt(data).create_branch()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
