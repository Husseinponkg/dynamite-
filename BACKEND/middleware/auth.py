from datetime import datetime, timedelta, timezone
import jwt
from models.models import userTokens
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent.parent / ".env")

# WARNING: Keep this secret safe in your environment variables (.env)
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "")
JWT_ALGORITHM = "HS256"

async def generate_user_token(user_id: int) -> str:
    """
    Generates a secure JWT token containing the unique user ID.
    The token automatically expires after 1 day.
    """
    # Define payload with the user's ID and token expiration time
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc)
    }
    
    # Encode and sign the JWT token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


async def verify_user_token(token: str) -> userTokens:
    """
    Decodes the JWT token and extracts the isolated user ID.
    Throws an error if the token is expired or altered.
    """
    try:
        # Decode and verify the signature/expiration automatically
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Return the verified user data wrapped in your Pydantic model
        return userTokens(id=int(payload["sub"]))
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid authentication token.")
