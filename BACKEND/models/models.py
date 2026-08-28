from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class createUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str
    full_name: str
    address: str


class userlogin(BaseModel):
    email: EmailStr
    password: str


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class ResendOTP(BaseModel):
    email: EmailStr


class userTokens(BaseModel):
    id: int


class deleteUserSchema(BaseModel):
    # Optional field in case you want verification, but the ID comes securely from the JWT
    confirm: bool = Field(default=True)


class updateUserSchema(BaseModel):
    # All update fields are optional so users can update only what they change
    username: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None


class SendOTP(BaseModel):
    email: EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class SendOTPToAll(BaseModel):
    pass


class BrevoConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_login: str
    smtp_key: str
