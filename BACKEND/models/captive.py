from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class CaptiveCheckout(BaseModel):
    package_id: int = Field(gt=0)
    router_id: Optional[int] = None
    phone_number: str = Field(min_length=9, max_length=15)
    payment_method: str = Field(description="mpesa, airtel, tigo, tigopesa, halotel, yas, cash")
    mac_address: Optional[str] = None


class CaptiveRedeem(BaseModel):
    voucher_code: str = Field(min_length=4, max_length=50)
    mac_address: Optional[str] = None
    phone: Optional[str] = None
