from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class VoucherStatus(str, Enum):
    active = "active"
    used = "used"
    expired = "expired"
    cancelled = "cancelled"


class GenerateVouchers(BaseModel):
    package_id: int = Field(gt=0)
    router_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=500)
    prefix: str = Field(default="DYN", max_length=10)
    code_length: int = Field(default=8, ge=6, le=16)
    expire_days: int = Field(default=30, ge=1, le=365)
    created_by: Optional[int] = None


class RedeemVoucher(BaseModel):
    voucher_code: str = Field(min_length=4, max_length=50)
    user_id: Optional[int] = None
    phone: Optional[str] = None
    mac_address: Optional[str] = None


class UpdateVoucherStatus(BaseModel):
    status: VoucherStatus


class VoucherFilter(BaseModel):
    status: Optional[VoucherStatus] = None
    package_id: Optional[int] = None
    router_id: Optional[int] = None
    search: Optional[str] = None
