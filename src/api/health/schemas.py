"""Pydantic schemas for the health domain."""

from pydantic import BaseModel, Field, ConfigDict


class CustomModel(BaseModel):
    """Custom base model for consistent serialization."""
    model_config = ConfigDict(
        populate_by_name=True,
    )


class HealthResponse(CustomModel):
    """Health check response model."""
    status: str = Field(..., description="Service status", max_length=32)
    timestamp: str = Field(..., description="Current timestamp")


class RootResponse(CustomModel):
    """Root endpoint response model."""
    name: str = Field(..., description="API name", max_length=256)
    version: str = Field(..., description="API version", max_length=32)
    status: str = Field(..., description="API status", max_length=32)
    endpoints: dict[str, str] = Field(..., description="Available endpoints")


class ErrorResponse(CustomModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message", max_length=1024)
