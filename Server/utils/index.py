from datetime import datetime, timezone
from uuid import uuid4


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
    ):
        self.status_code = status_code
        self.message = message

        super().__init__(message)


def get_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)