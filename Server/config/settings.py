from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pastor's Pulpit API"

    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 5000

    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_database: str = "Pulpit"

    client_url: str = "http://localhost:5173"

    master_password: str | None = None
    master_otp: str | None = None

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@localhost"

    otp_expiry_minutes: int = 10
    password_reset_expiry_minutes: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
