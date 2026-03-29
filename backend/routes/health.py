"""
health.py - /health route.
Returns the API status and timestamp for uptime monitoring.
"""

from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="API health check",
    description="Returns the current health status and timestamp of the ASPRAMS API.",
)
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "ASPRAMS API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
