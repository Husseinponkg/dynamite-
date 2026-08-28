from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from decimal import Decimal


class WithdrawMethod(str, Enum):
    mpesa = "mpesa"
    airtel = "airtel"
    tigo = "tigo"
    halotel = "halotel"
    bank_transfer = "bank_transfer"
    cash = "cash"


class WithdrawStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    rejected = "rejected"
    cancelled = "cancelled"


class CreateWithdraw(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    method: WithdrawMethod = WithdrawMethod.mpesa
    account_number: str = Field(min_length=5, max_length=50)
    account_name: Optional[str] = None
    notes: Optional[str] = None
    admin_id: Optional[int] = None


class UpdateWithdraw(BaseModel):
    status: WithdrawStatus
    notes: Optional[str] = None
    processed_by: Optional[int] = None
