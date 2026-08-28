import os
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


ENCRYPTION_KEY = os.getenv("ROUTER_ENCRYPTION_KEY")


if not ENCRYPTION_KEY:
    raise RuntimeError(
        "ROUTER_ENCRYPTION_KEY is not configured"
    )


fernet = Fernet(
    ENCRYPTION_KEY.encode()
)


def encrypt_value(value: str | None):

    if not value:
        return None

    return fernet.encrypt(
        value.encode()
    ).decode()


def decrypt_value(value: str | None):

    if not value:
        return None

    return fernet.decrypt(
        value.encode()
    ).decode()
