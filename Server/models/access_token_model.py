from pydantic import BaseModel


class AuthContext(BaseModel):
    user_id: str
    token_hash: str