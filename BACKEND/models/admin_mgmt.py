from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class AdminRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    support = "support"


class CreateAdmin(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    role: AdminRole = AdminRole.admin


class UpdateAdmin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[AdminRole] = None
    status: Optional[str] = None
    password: Optional[str] = None


class CreateBranch(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: Optional[str] = None
    manager_name: Optional[str] = None
    phone: Optional[str] = None
    status: str = "active"


class UpdateBranch(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    manager_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
