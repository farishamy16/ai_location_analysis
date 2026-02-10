"""Pydantic schemas for the complaints domain."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


class CustomModel(BaseModel):
    """Custom base model for consistent serialization."""
    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserInfo(CustomModel):
    """User information model."""
    name: Optional[str] = Field(None, description="User's name", max_length=256)
    email: Optional[EmailStr] = Field(None, description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number", max_length=32)


class ComplaintRequest(CustomModel):
    """Request model for complaint submission."""
    complaint: str = Field(..., description="The complaint text", min_length=1, max_length=10000)
    user_info: Optional[UserInfo] = Field(None, description="Optional user information")


class LocationData(CustomModel):
    """Location data model."""
    place_name: Optional[str] = Field(None, description="Extracted place name", max_length=512)
    formatted_address: Optional[str] = Field(None, description="Formatted address", max_length=512)
    lat: Optional[float] = Field(None, description="Latitude coordinate", ge=-90, le=90)
    lng: Optional[float] = Field(None, description="Longitude coordinate", ge=-180, le=180)


class DepartmentInfo(CustomModel):
    """Department information model."""
    id: str = Field(..., description="Department ID")
    name: str = Field(..., description="Department name", max_length=256)
    email: EmailStr = Field(..., description="Department email address")
    phone: str = Field(..., description="Department phone number", max_length=32)
    categories: list[str] = Field(..., description="List of categories handled by department")


class ClassificationData(CustomModel):
    """Classification data model."""
    category: str = Field(..., description="Complaint category", max_length=128)
    severity: str = Field(..., description="Severity level", max_length=32)
    urgency: str = Field(..., description="Urgency level", max_length=32)
    summary: Optional[str] = Field(None, description="Complaint summary", max_length=1024)
    keywords: Optional[list[str]] = Field(None, description="Extracted keywords")
    confidence: Optional[float] = Field(None, description="Classification confidence", ge=0, le=1)
    classification_method: Optional[str] = Field(None, description="Method used for classification", max_length=64)
    classification_confidence: Optional[float] = Field(None, description="Classification confidence score", ge=0, le=1)
    llm_category: Optional[str] = Field(None, description="LLM classified category", max_length=128)
    semantic_category: Optional[str] = Field(None, description="Semantic matched category", max_length=128)
    all_scores: Optional[Dict[str, float]] = Field(None, description="All classification scores")


class RoutingResult(CustomModel):
    """Routing result model."""
    ticket_id: str = Field(..., description="Generated ticket ID")
    department: DepartmentInfo = Field(..., description="Routed department information")
    priority: str = Field(..., description="Ticket priority", max_length=32)
    estimated_response_hours: int = Field(..., description="Estimated response time in hours", ge=0)
    classification: ClassificationData = Field(..., description="Classification result")
    user_info: Dict[str, Any] = Field(..., description="User information")
    routed_at: str = Field(..., description="Timestamp when complaint was routed")


class NotificationStatus(CustomModel):
    """Notification status model."""
    department_notification_sent: bool = Field(..., description="Whether department notification was sent")
    user_confirmation_sent: bool = Field(..., description="Whether user confirmation was sent")
    department_notification_error: Optional[str] = Field(None, description="Error message if department notification failed", max_length=1024)
    user_notification_error: Optional[str] = Field(None, description="Error message if user notification failed", max_length=1024)


class ComplaintResponse(CustomModel):
    """Complete complaint response model containing all outputs."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message", max_length=512)
    timestamp: str = Field(..., description="Response timestamp")
    location_data: Optional[LocationData] = Field(None, description="Extracted location data")
    routing_result: Optional[RoutingResult] = Field(None, description="Routing result with classification")
    notification_status: Optional[NotificationStatus] = Field(None, description="Notification status")


class ErrorResponse(CustomModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message", max_length=1024)
