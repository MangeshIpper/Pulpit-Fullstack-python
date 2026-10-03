from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class VerifyOTPRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class ResendOTPRequest(BaseModel):
    email: EmailStr
