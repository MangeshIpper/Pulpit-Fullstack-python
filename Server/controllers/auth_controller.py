from services import user_service


async def signup(data):
    return await user_service.signup(data)


async def verify_otp(data):
    return await user_service.verify_otp(data)


async def resend_otp(data):
    return await user_service.resend_otp(data)


async def signin(data):
    return await user_service.signin(data)


async def forgot_password(data):
    return await user_service.forgot_password(data)


async def reset_password(data):
    return await user_service.reset_password(data)
