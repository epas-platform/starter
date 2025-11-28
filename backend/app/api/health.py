"""Health check endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DB
from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    profile: str


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str
    database: str
    redis: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check - is the service running?"""
    from app import __version__

    settings = get_settings()

    return HealthResponse(
        status="healthy",
        version=__version__,
        profile=settings.profile,
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(db: DB) -> ReadyResponse:
    """Readiness check - can the service handle requests?

    Checks database and cache connectivity.
    """
    # Check database
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        pass

    # Check Redis (basic ping)
    redis_status = "unhealthy"
    try:
        import redis.asyncio as redis

        settings = get_settings()
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        redis_status = "healthy"
    except Exception:
        pass

    overall_status = "ready" if db_status == "healthy" else "not_ready"

    return ReadyResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
    )
