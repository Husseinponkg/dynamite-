from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InitiatePay(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user making the payment")
    package_id: int = Field(..., gt=0, description="ID of the package being purchased")
    router_id: int = Field(..., gt=0, description="ID of the router associated with the package")
    payment_method: str = Field(..., description="e.g., TIGO, AIRTEL, MPESA, HALOPESA, CASH")
    phone_number: str = Field(..., description="Format: 255XXXXXXXXX")
    reference_number: str = Field(..., description="Your internal unique system reference id")
    notes: Optional[str] = None

class AzamPayCallback(BaseModel):
    externalreference: str
    transactionstatus: str
    transid: Optional[str] = None
    mnoreference: Optional[str] = None
    reference: Optional[str] = None
    utilityref: Optional[str] = None
    amount: Optional[str] = None

class PaymentCallback(BaseModel):
    id: str
    msisdn: str
    amount: float
    status: str
    reference: str
    utilityref: str
    operator: str
    timestamp: str

class PaymentUpdate(BaseModel):
    status: str
    completed_at: Optional[datetime] = None

class PaymentStatus(BaseModel):
    reference_number: str
