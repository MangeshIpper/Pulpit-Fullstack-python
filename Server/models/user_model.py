from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class SignupRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    phoneNumber: str = Field(
        min_length=5,
        max_length=30,
    )

    officePhone: str | None = None

    churchName: str | None = None


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class ProfileUpdateRequest(BaseModel):
    name: str | None = None

    phoneNumber: str | None = None

    officePhone: str | None = None

    churchName: str | None = None

    about: str | None = None

    picUrl: str | None = None

    isDarkMode: bool | None = None
