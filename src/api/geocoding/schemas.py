"""Pydantic schemas for the geocoding domain."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CustomModel(BaseModel):
    """Custom base model for consistent serialization."""
    model_config = ConfigDict(
        populate_by_name=True,
    )


class GeocodingRequest(CustomModel):
    """Request model for geocoding an address."""
    address: str = Field(..., description="The address or place name to geocode", min_length=1, max_length=1024)


class GeocodingResponse(CustomModel):
    """Response model for geocoding results."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message", max_length=512)
    timestamp: str = Field(..., description="Response timestamp")
    lat: Optional[float] = Field(None, description="Latitude coordinate", ge=-90, le=90)
    lng: Optional[float] = Field(None, description="Longitude coordinate", ge=-180, le=180)
    formatted_address: Optional[str] = Field(None, description="Formatted address from the API", max_length=512)
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw response data from the API")


class ErrorResponse(CustomModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message", max_length=1024)


class GeocodingV2Response(CustomModel):
    """Response model for geocoding results with simplified address components."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message", max_length=512)
    timestamp: str = Field(..., description="Response timestamp")
    formatted_address: Optional[str] = Field(None, description="Formatted address from the API", max_length=512)
    jalan: Optional[str] = Field(None, description="Street name (Jalan)", max_length=512)
    poskod: Optional[str] = Field(None, description="Postal code (Poskod)", max_length=32)
    negeri: Optional[str] = Field(None, description="State (Negeri)", max_length=256)
    daerah: Optional[str] = Field(None, description="District (Daerah)", max_length=256)
    bandar: Optional[str] = Field(None, description="City (Bandar)", max_length=256)
