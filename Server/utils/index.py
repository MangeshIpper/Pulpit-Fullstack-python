import hashlib
import secrets

import bcrypt


def hash_password(
    password: str,
) -> str:

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise AppError(
            400,
            "Password cannot exceed 72 UTF-8 bytes.",
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    except ValueError:
        return False


def generate_otp() -> str:
    return str(secrets.randbelow(900_000) + 100_000)


def generate_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(
    token: str,
) -> str:

    return hashlib.sha256(token.encode("utf-8")).hexdigest()
