import httpx
from typing import Dict, Any
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

AZAMPAY_BASE_URL = os.getenv("AZAM_API")
AZAMPAY_AUTH_URL = os.getenv("AZAM_AUTH_URL")
AZAMPAY_CLIENT_ID = os.getenv("AZAM_CLIENT_ID")
AZAMPAY_CLIENT_SECRET = os.getenv("AZAM_CLIENT_SECRET_KEY")
AZAMPAY_APP_NAME = os.getenv("azam_app_name")
AZAMPAY_TOKEN_FALLBACK = os.getenv("AZAM_TOKEN")

logger = logging.getLogger(__name__)

def _provider_for_method(method: str) -> str:
    """Maps frontend method values to AzamPay acceptable operators."""
    method_upper = method.upper()
    mapping = {
        "MPESA": "VodaCom",
        "TIGO": "Tigo",
        "AIRTEL": "Airtel",
        "HALOPESA": "HaloPesa"
    }
    return mapping.get(method_upper, "AzamPay")

async def get_azampay_token() -> str:
    """Fetches bearer token required for AzamPay requests."""
    url = f"{AZAMPAY_AUTH_URL}/api/v1/Authenticator/token"
    payload = {
        "clientId": AZAMPAY_CLIENT_ID,
        "clientSecret": AZAMPAY_CLIENT_SECRET,
        "appName": AZAMPAY_APP_NAME,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                return token
        if AZAMPAY_TOKEN_FALLBACK:
            return AZAMPAY_TOKEN_FALLBACK
        raise Exception(f"Failed to authenticate with AzamPay: {response.text}")

async def initiate_azampay_payment(amount: float, phone_number: str, external_id: str, provider: str) -> Dict[str, Any]:
    """Triggers the USSD push to the user's mobile device."""
    token = await get_azampay_token()
    url = f"{AZAMPAY_BASE_URL}/api/v1/Partner/Collection/MnoCheckout"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "amount": str(amount),
        "msisdn": phone_number,
        "operator": provider,
        "externalId": external_id,
        "currency": "TZS",
        "appName": AZAMPAY_APP_NAME,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            res_data = response.json()
            
            if response.status_code == 200 and res_data.get("success") is True:
                return {
                    "success": True,
                    "transaction_id": res_data.get("transactionId", external_id)
                }
            return {"success": False, "transaction_id": external_id, "error": response.text}
        except Exception as e:
            logger.error(f"AzamPay request failure: {str(e)}")
            return {"success": False, "transaction_id": external_id, "error": str(e)}

async def check_azampay_payment_status(transaction_id: str) -> str:
    """Manually fetches state fallback checking."""
    token = await get_azampay_token()
    url = f"{AZAMPAY_BASE_URL}/api/v1/Partner/Collection/TransactionStatus?id={transaction_id}"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("status", "PENDING")
        return "UNKNOWN"
