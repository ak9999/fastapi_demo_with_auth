"""Health check endpoints for container orchestration.

Liveness probe: tells the platform if the process is still running (restart if down).
Readiness probe: tells the platform if the app is ready to accept traffic (remove from LB if not).
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    message: str


@router.get("/live", response_model=HealthResponse, status_code=200)
async def liveness() -> HealthResponse:
    """Liveness probe: returns 200 if the process is running.

    Status code 200 is implicit for FastAPI GET endpoints, but made explicit here for clarity.
    The orchestrator restarts the container if this fails.
    """
    return HealthResponse(status="healthy", message="Application is alive")


@router.get("/ready", response_model=HealthResponse, status_code=200)
async def readiness() -> HealthResponse:
    """Readiness probe: returns 200 if the app can handle requests.

    Status code 200 is implicit for FastAPI GET endpoints, but made explicit here for clarity.
    Extend this to check dependencies (database, external services, etc).
    The orchestrator removes the container from load balancing if this fails.
    """
    return HealthResponse(
        status="ready", message="Application is ready to serve requests"
    )
