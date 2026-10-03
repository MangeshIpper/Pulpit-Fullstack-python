from datetime import timedelta

from fastapi import (
    Depends,
    HTTPException,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from config.database import get_database
from models.access_token_model import AuthContext

from utils.index import (
    generate_token,
    hash_token,
    utc_now,
)

bearer_scheme = HTTPBearer(auto_error=False)


async def create_access_token(
    user_id: str,
) -> str:

    database = get_database()

    raw_token = generate_token()

    token_hash = hash_token(raw_token)

    await database.accessTokens.insert_one(
        {
            "userId": user_id,
            "tokenHash": token_hash,
            "createdAt": utc_now(),
        }
    )

    return raw_token


async def remove_access_token(
    token_hash: str,
) -> None:

    database = get_database()

    await database.accessTokens.delete_one({"tokenHash": token_hash})


async def remove_all_user_tokens(
    user_id: str,
) -> None:

    database = get_database()

    await database.accessTokens.delete_many({"userId": user_id})


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthContext:

    if credentials is None:

        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    raw_token = credentials.credentials

    token_hash = hash_token(raw_token)

    database = get_database()

    access_token = await database.accessTokens.find_one({"tokenHash": token_hash})

    if access_token is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid access token.",
        )

    return AuthContext(
        user_id=access_token["userId"],
        token_hash=token_hash,
    )
