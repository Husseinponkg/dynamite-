from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum


class PackageStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class CreatePackages(BaseModel):
    package_name: str = Field(min_length=1, max_length=100)
    package_desc: str | None = None
    price: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    validity_days: int = Field(ge=0)
    validity_hours: int = Field(default=0, ge=0, le=23)
    bandwidth_up: int = Field(default=0, ge=0)
    bandwidth_down: int = Field(default=0, ge=0)
    data_limit: int = Field(default=0, ge=0)
    concurrent_logins: int = Field(default=1, ge=1)
    status: PackageStatus = PackageStatus.active


class UpdatePackages(BaseModel):
    package_name: str | None = Field(default=None, min_length=1, max_length=100)
    package_desc: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    validity_days: int | None = Field(default=None, ge=0)
    validity_hours: int | None = Field(default=None, ge=0, le=23)
    bandwidth_up: int | None = Field(default=None, ge=0)
    bandwidth_down: int | None = Field(default=None, ge=0)
    data_limit: int | None = Field(default=None, ge=0)
    concurrent_logins: int | None = Field(default=None, ge=1)
    status: PackageStatus | None = None
