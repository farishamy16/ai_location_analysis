"""Router for the health domain."""

from datetime import datetime
from fastapi import APIRouter, status

from src.api.health import constants
from src.api.health.schemas import HealthResponse, RootResponse, ErrorResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    description="Root endpoint with API information",
    tags=[constants.TAG_HEALTH],
    responses={
        status.HTTP_200_OK: {"model": RootResponse},
    },
)
async def root():
    """Root endpoint with API information."""
    return RootResponse(
        name=constants.API_NAME,
        version=constants.API_VERSION,
        status=constants.API_STATUS,
        endpoints={
            "POST /api/complaint": "Submit a complaint and get full analysis",
            "GET /health": "Health check endpoint"
        }
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    description="Health check endpoint",
    tags=[constants.TAG_HEALTH],
    responses={
        status.HTTP_200_OK: {"model": HealthResponse},
    },
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status=constants.STATUS_HEALTHY,
        timestamp=datetime.now().isoformat()
    )
