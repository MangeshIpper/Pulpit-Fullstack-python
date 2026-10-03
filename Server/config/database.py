from typing import Any
from pymongo import AsyncMongoClient
from config.settings import settings

client: AsyncMongoClient[dict[str, Any]] | None = None
database = None


async def connect_database() -> None:
    global client
    global database

    client = AsyncMongoClient(settings.mongodb_uri)

    # Actually contact MongoDB.
    await client.admin.command("ping")

    database = client[settings.mongodb_database]

    print(f"✅ MongoDB connected: " f"{settings.mongodb_database}")


async def disconnect_database() -> None:
    global client
    global database

    if client is not None:
        await client.close()

    client = None
    database = None

    print("🛑 MongoDB disconnected")


def get_database():
    if database is None:
        raise RuntimeError("MongoDB has not been initialized.")

    return database
