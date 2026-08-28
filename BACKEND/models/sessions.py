from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateSession(BaseModel):
    user_id: Optional[int] = None
    router_id: int = Field(gt=0)
    session_id: str = Field(min_length=1, max_length=255)
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    username: Optional[str] = None  # hotspot username / voucher code


class EndSession(BaseModel):
    session_id: str
    bandwidth_up_used: Optional[int] = 0
    bandwidth_down_used: Optional[int] = 0
