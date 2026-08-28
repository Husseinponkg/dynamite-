from pydantic import BaseModel
from typing import Optional


class createrouting(BaseModel):

    router_name: str

    router_ip: str

    router_port: int = 8728

    username: Optional[str] = None

    password: Optional[str] = None

    connection_type: str = "api"

    api_type: Optional[str] = None

    api_url: Optional[str] = None

    api_username: Optional[str] = None

    api_password: Optional[str] = None

    api_key: Optional[str] = None

    api_token: Optional[str] = None

    location: Optional[str] = None

    max_users: int = 500

class statusview(BaseModel):
    router_id: int