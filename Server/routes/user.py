from fastapi import (
    APIRouter,
    Depends,
)

from controllers import (
    auth_controller,
    user_controller,
)

from models.access_token_model import (
    AuthContext,
)

from models.email_verification_model import (
    ResendOTPRequest,
    VerifyOTPRequest,
)

from models.user_model import (
    ForgotPasswordRequest,
    ProfileUpdateRequest,
    ResetPasswordRequest,
    SigninRequest,
    SignupRequest,
)

from services.access_token_service import (
    require_auth,
)

router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.post("/signup")
async def signup(
    data: SignupRequest,
):
    return await auth_controller.signup(data)


@router.post("/verifyOTP")
async def verify_otp(
    data: VerifyOTPRequest,
):
    return await auth_controller.verify_otp(data)


@router.post("/resendOTP")
async def resend_otp(
    data: ResendOTPRequest,
):
    return await auth_controller.resend_otp(data)


@router.post("/signin")
async def signin(
    data: SigninRequest,
):
    return await auth_controller.signin(data)


@router.post("/forgotPassword")
async def forgot_password(
    data: ForgotPasswordRequest,
):
    return await auth_controller.forgot_password(data)


@router.post("/resetPassword")
async def reset_password(
    data: ResetPasswordRequest,
):
    return await auth_controller.reset_password(data)


@router.get("/profile")
async def get_profile(
    auth: AuthContext = Depends(require_auth),
):
    return await user_controller.get_profile(auth.user_id)


@router.post("/profile")
async def update_profile(
    data: ProfileUpdateRequest,
    auth: AuthContext = Depends(require_auth),
):
    return await user_controller.update_profile(
        auth.user_id,
        data,
    )


@router.post("/logout")
async def logout(
    auth: AuthContext = Depends(require_auth),
):
    return await user_controller.logout(auth.token_hash)
