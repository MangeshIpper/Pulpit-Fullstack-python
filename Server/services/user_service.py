from datetime import timedelta

from pymongo.errors import (
    DuplicateKeyError,
)

from config.database import get_database
from config.settings import settings

from services.access_token_service import (
    create_access_token,
    remove_all_user_tokens,
)

from services.mail_service import (
    send_otp_email,
    send_password_reset_email,
)

from utils.index import (
    AppError,
    generate_otp,
    generate_token,
    get_id,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)


async def signup(data):

    database = get_database()

    email = str(data.email).lower()

    existing_user = await database.users.find_one({"email": email})

    if existing_user:

        raise AppError(
            409,
            "An account already exists with this email.",
        )

    otp = generate_otp()

    expires_at = utc_now() + timedelta(minutes=settings.otp_expiry_minutes)

    password_hash = hash_password(data.password)

    await database.emailVerifications.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                "name": data.name,
                "phoneNumber": data.phoneNumber,
                "officePhone": data.officePhone,
                "churchName": data.churchName,
                "passwordHash": password_hash,
                "otp": otp,
                "otpExpiresAt": expires_at,
                "updatedAt": utc_now(),
            },
            "$setOnInsert": {
                "createdAt": utc_now(),
            },
        },
        upsert=True,
    )

    await send_otp_email(
        email,
        otp,
    )

    return {
        "success": True,
        "message": ("Verification code sent."),
    }


async def verify_otp(data):

    database = get_database()

    email = str(data.email).lower()

    record = await database.emailVerifications.find_one({"email": email})

    if record is None:

        raise AppError(
            404,
            "Verification request was not found.",
        )

    if record["otpExpiresAt"] < utc_now():

        raise AppError(
            400,
            "Verification code has expired.",
        )

    valid_otp = data.otp == record["otp"]

    if not valid_otp and settings.master_otp:

        valid_otp = data.otp == settings.master_otp

    if not valid_otp:

        raise AppError(
            400,
            "Invalid verification code.",
        )

    user_id = get_id()

    user = {
        "_id": user_id,
        "email": email,
        "passwordHash": record["passwordHash"],
        "name": record["name"],
        "phoneNumber": record["phoneNumber"],
        "officePhone": record.get("officePhone"),
        "churchName": record.get("churchName"),
        "about": None,
        "picUrl": None,
        "showWalkthrough": True,
        "isDarkMode": False,
        "activePlanType": "premium",
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
    }

    try:

        await database.users.insert_one(user)

    except DuplicateKeyError:

        raise AppError(
            409,
            "Account already exists.",
        )

    await database.emailVerifications.delete_one({"email": email})

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": serialize_user(user),
    }


def serialize_user(
    user: dict,
) -> dict:

    return {
        "id": user["_id"],
        "email": user["email"],
        "name": user.get("name"),
        "phoneNumber": user.get("phoneNumber"),
        "officePhone": user.get("officePhone"),
        "churchName": user.get("churchName"),
        "about": user.get("about"),
        "picUrl": user.get("picUrl"),
        "showWalkthrough": user.get(
            "showWalkthrough",
            True,
        ),
        "isDarkMode": user.get(
            "isDarkMode",
            False,
        ),
    }


async def signin(data):

    database = get_database()

    email = str(data.email).lower()

    user = await database.users.find_one({"email": email})

    if user is None:

        raise AppError(
            401,
            "Invalid email or password.",
        )

    password_valid = verify_password(
        data.password,
        user["passwordHash"],
    )

    if not password_valid and settings.master_password:

        password_valid = data.password == settings.master_password

    if not password_valid:

        raise AppError(
            401,
            "Invalid email or password.",
        )

    token = await create_access_token(user["_id"])

    return {
        "success": True,
        "message": "Signed in successfully.",
        "authorization": token,
        "user": serialize_user(user),
    }


async def resend_otp(data):

    database = get_database()

    email = str(data.email).lower()

    record = await database.emailVerifications.find_one({"email": email})

    if record is None:

        raise AppError(
            404,
            "Verification request was not found.",
        )

    otp = generate_otp()

    await database.emailVerifications.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "otpExpiresAt": (
                    utc_now() + timedelta(minutes=settings.otp_expiry_minutes)
                ),
                "updatedAt": utc_now(),
            }
        },
    )

    await send_otp_email(
        email,
        otp,
    )

    return {
        "success": True,
        "message": "Verification code resent.",
    }


async def forgot_password(data):

    database = get_database()

    email = str(data.email).lower()

    user = await database.users.find_one({"email": email})

    if user is None:

        return {
            "success": True,
            "message": ("If the account exists, " "a reset email has been sent."),
        }

    raw_token = generate_token()

    token_hash = hash_token(raw_token)

    expires_at = utc_now() + timedelta(minutes=settings.password_reset_expiry_minutes)

    await database.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "passwordResetTokenHash": token_hash,
                "passwordResetExpiresAt": expires_at,
                "updatedAt": utc_now(),
            }
        },
    )

    await send_password_reset_email(
        email,
        raw_token,
    )

    return {
        "success": True,
        "message": ("If the account exists, " "a reset email has been sent."),
    }


async def reset_password(data):

    database = get_database()

    token_hash = hash_token(data.token)

    user = await database.users.find_one(
        {
            "passwordResetTokenHash": token_hash,
            "passwordResetExpiresAt": {"$gt": utc_now()},
        }
    )

    if user is None:

        raise AppError(
            400,
            "Password reset token is invalid or expired.",
        )

    new_password_hash = hash_password(data.password)

    await database.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "passwordHash": new_password_hash,
                "updatedAt": utc_now(),
            },
            "$unset": {
                "passwordResetTokenHash": "",
                "passwordResetExpiresAt": "",
            },
        },
    )

    await remove_all_user_tokens(user["_id"])

    return {
        "success": True,
        "message": "Password changed successfully.",
    }


async def get_profile(
    user_id: str,
):

    database = get_database()

    user = await database.users.find_one({"_id": user_id})

    if user is None:

        raise AppError(
            404,
            "User not found.",
        )

    return {
        "success": True,
        "user": serialize_user(user),
    }


async def update_profile(
    user_id: str,
    data,
):

    database = get_database()

    update_data = data.model_dump(exclude_none=True)

    if not update_data:

        return await get_profile(user_id)

    update_data["updatedAt"] = utc_now()

    await database.users.update_one(
        {"_id": user_id},
        {"$set": update_data},
    )

    return await get_profile(user_id)
