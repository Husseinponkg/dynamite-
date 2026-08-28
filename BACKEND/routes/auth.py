from fastapi import APIRouter, Depends, HTTPException, status
from controllers.auth import Authentication
from middleware.auth import generate_user_token, verify_user_token
from models.models import (
    createUser,
    userlogin,
    VerifyOTP,
    ResendOTP,
    SendOTP,
    ForgotPassword,
    ResetPassword,
    SendOTPToAll,
    updateUserSchema,
    deleteUserSchema
)

router = APIRouter()

# =====================================================
# REGISTER & LOGIN
# =====================================================

@router.post("/register")
async def register(data: createUser):
    auth = Authentication(data)
    return await auth.registeruser()


@router.post("/verify-otp")
async def verify_otp(data: VerifyOTP):
    auth = Authentication(data)
    return await auth.verifyotp()


@router.post("/login")
async def login(data: userlogin):
    auth = Authentication(data)
    result = await auth.loginuser()

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    token = await generate_user_token(result["user"]["id"])

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": result["user"]
    }

# =====================================================
# OTP & PASSWORD RESET
# =====================================================

@router.post("/resend-otp")
async def resend_otp(data: ResendOTP):
    auth = Authentication(data)
    return await auth.resendotp()


@router.post("/send-otp")
async def send_otp(data: SendOTP):
    auth = Authentication(data)
    return await auth.send_otp()


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword):
    auth = Authentication(data)
    return await auth.forgotpassword()


@router.post("/reset-password")
async def reset_password(data: ResetPassword):
    auth = Authentication(data)
    return await auth.resetpassword()


@router.get("/brevo-status")
async def brevo_status():
    auth = Authentication()
    return auth.brevo_status()

# =====================================================
# USERS
# =====================================================

@router.get("/users")
async def get_all_users():
    auth = Authentication()
    result = await auth.getallusers()
    return {"success": True, "users": result}


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    auth = Authentication()
    result = await auth.getuser(user_id=user_id)
    return result


@router.post("/send-otp-to-all")
async def send_otp_to_all():
    auth = Authentication()
    return await auth.send_otp_email_to_all()

# =====================================================
# PROTECTED ISOLATED ENDPOINTS
# =====================================================

@router.put("/profile/update")
async def update_profile(
    data: updateUserSchema,
    current_user: dict = Depends(verify_user_token)
):
    auth = Authentication(data)
    return await auth.updateuser(current_user_id=current_user["id"])


@router.delete("/profile/delete")
async def delete_profile(
    data: deleteUserSchema,
    current_user: dict = Depends(verify_user_token)
):
    auth = Authentication(data)
    return await auth.deleteuser(current_user_id=current_user["id"])
