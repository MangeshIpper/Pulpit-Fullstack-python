from fastapi import APIRouter

from config.database import get_database


router = APIRouter()


@router.get("/api/v1/health")
async def health():
    database = get_database()

    await database.command("ping")

    return {
        "success": True,
        "status": "ok",
        "service": "pastors-pulpit-api",
        "database": "connected",
    }