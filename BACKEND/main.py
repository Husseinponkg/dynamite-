
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.router import router as router_api
from routes.packages import router as packages_api
from routes.payments import router as payments_api
from routes.vouchers import router as vouchers_api
from routes.sessions import router as sessions_api
from routes.income import router as income_api
from routes.withdraws import router as withdraws_api
from routes.admin_mgmt import router as admin_api
from routes.captive import router as captive_api

import os


app = FastAPI(
    title="Dynamite Networks",
    description="Modern ISP Hotspot Billing System",
    version="2.1.0",
)


# =====================================================
# CORS
# =====================================================

frontend_url = os.getenv("FRONTEND_URL", "").strip()

origins = [
    "https://dynamite-wine.vercel.app",
]

if frontend_url and frontend_url not in origins:
    origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# ROUTES
# =====================================================

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    router_api,
    prefix="/routing",
    tags=["Routers"],
)

app.include_router(
    packages_api,
    prefix="/packages",
    tags=["Packages"],
)

# payments router already contains /payments prefix
app.include_router(
    payments_api,
    tags=["Payments"],
)

app.include_router(
    vouchers_api,
    prefix="/vouchers",
    tags=["Vouchers"],
)

app.include_router(
    sessions_api,
    prefix="/sessions",
    tags=["Sessions"],
)

app.include_router(
    income_api,
    prefix="/income",
    tags=["Income"],
)

app.include_router(
    withdraws_api,
    prefix="/withdraws",
    tags=["Withdraws"],
)

app.include_router(
    admin_api,
    prefix="/admin",
    tags=["Admin"],
)

app.include_router(
    captive_api,
    prefix="/captive",
    tags=["Captive Portal"],
)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Dynamite Networks Billing",
        "version": "2.1.0",
    }


# =====================================================
# LOCAL DEVELOPMENT
# =====================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("APP_ENV") == "development",
    )
