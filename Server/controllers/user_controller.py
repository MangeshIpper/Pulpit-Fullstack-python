from services import user_service
from services.access_token_service import (
    remove_access_token,
)


async def get_profile(
    user_id: str,
):
    return await user_service.get_profile(user_id)


async def update_profile(
    user_id: str,
    data,
):
    return await user_service.update_profile(
        user_id,
        data,
    )


async def logout(
    token_hash: str,
):

    await remove_access_token(token_hash)

    return {
        "success": True,
        "message": "Logged out successfully.",
    }
