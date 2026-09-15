"""Точка входа FastAPI-приложения TrafficMaster Pro."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import settings

APP_VERSION = "0.1.0"

app = FastAPI(
    title="TrafficMaster Pro API",
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    """Возвращает краткую информацию о сервисе.

    Returns:
        Словарь с именем сервиса, версией, окружением и ссылкой на docs.
    """
    return {
        "service": "TrafficMaster Pro API",
        "version": APP_VERSION,
        "environment": settings.environment,
        "docs": "/api/docs",
    }
