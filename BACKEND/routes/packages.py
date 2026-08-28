from fastapi import APIRouter, HTTPException

from models.packages import CreatePackages, UpdatePackages
from controllers.packages import Packages


router = APIRouter(tags=["Packages"])


@router.post("/create")
async def create_package(data: CreatePackages):
    return await Packages(data).packageCreation()


@router.get("/")
async def get_all_packages():
    return await Packages().getAllPackages()


@router.get("/{package_id}")
async def get_one_package(package_id: int):
    result = await Packages().getOnePackage(package_id)
    if result.get("message") == "Package not found":
        raise HTTPException(status_code=404, detail="Package not found")
    return result


@router.put("/{package_id}")
async def update_package(package_id: int, data: UpdatePackages):
    result = await Packages(data).updatePackage(package_id)
    if result.get("message") == "Package not found":
        raise HTTPException(status_code=404, detail="Package not found")
    return result


@router.delete("/{package_id}")
async def delete_package(package_id: int):
    result = await Packages().deletePackage(package_id)
    if result.get("message") == "Package not found":
        raise HTTPException(status_code=404, detail="Package not found")
    return result
