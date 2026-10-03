from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.database import (
    connect_database,
    create_indexes,
    disconnect_database,
)
from config.settings import settings

from routes.index import router as index_router

from utils.error import AppError
from routes.user import (
    router as user_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await connect_database()

    await create_indexes()

    yield

    await disconnect_database()


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.client_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    error: AppError,
):
    return JSONResponse(
        status_code=error.status_code,
        content={
            "success": False,
            "message": error.message,
        },
    )


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Pastor's Pulpit API",
    }


app.include_router(index_router)
app.include_router(user_router)
