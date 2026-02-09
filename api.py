"""
FastAPI application for the Complaint Location Analyzer.
Provides REST API endpoints for complaint submission and analysis.
"""

from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from src.analyzers.complaint import ComplaintAnalyzer
from src.services.router import ComplaintRouter
from src.services.notifier import NotificationService
from src.config.settings import settings


# Initialize FastAPI app
app = FastAPI(
    title="Complaint Location Analyzer API",
    description="AI-powered complaint location analyzer with routing and notification capabilities",
    version="1.0.0"
)


# Pydantic models for request/response
class UserInfo(BaseModel):
    """User information model."""
    name: Optional[str] = Field(None, description="User's name")
    email: Optional[str] = Field(None, description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")


class ComplaintRequest(BaseModel):
    """Request model for complaint submission."""
    complaint: str = Field(..., description="The complaint text", min_length=1)
    user_info: Optional[UserInfo] = Field(None, description="Optional user information")


class LocationData(BaseModel):
    """Location data model."""
    place_name: Optional[str] = Field(None, description="Extracted place name")
    formatted_address: Optional[str] = Field(None, description="Formatted address")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lng: Optional[float] = Field(None, description="Longitude coordinate")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw geocoding data")


class DepartmentInfo(BaseModel):
    """Department information model."""
    id: str
    name: str
    email: str
    phone: str
    categories: list[str]


class ClassificationData(BaseModel):
    """Classification data model."""
    category: str
    severity: str
    urgency: str
    summary: Optional[str] = None
    keywords: Optional[list[str]] = None
    confidence: Optional[float] = None
    classification_method: Optional[str] = None
    classification_confidence: Optional[float] = None
    llm_category: Optional[str] = None
    semantic_category: Optional[str] = None
    all_scores: Optional[Dict[str, float]] = None


class RoutingResult(BaseModel):
    """Routing result model."""
    ticket_id: str
    department: DepartmentInfo
    priority: str
    estimated_response_hours: int
    classification: ClassificationData
    location: Dict[str, Any]
    user_info: Dict[str, Any]
    routed_at: str


class NotificationStatus(BaseModel):
    """Notification status model."""
    department_notification_sent: bool = Field(..., description="Whether department notification was sent")
    user_confirmation_sent: bool = Field(..., description="Whether user confirmation was sent")
    department_notification_error: Optional[str] = Field(None, description="Error message if department notification failed")
    user_notification_error: Optional[str] = Field(None, description="Error message if user notification failed")


class ComplaintResponse(BaseModel):
    """Complete complaint response model containing all outputs."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    timestamp: str = Field(..., description="Response timestamp")
    location_data: Optional[LocationData] = Field(None, description="Extracted location data")
    routing_result: Optional[RoutingResult] = Field(None, description="Routing result with classification")
    notification_status: Optional[NotificationStatus] = Field(None, description="Notification status")


# Initialize services (lazy initialization on first request)
_analyzer: Optional[ComplaintAnalyzer] = None
_router: Optional[ComplaintRouter] = None
_notifier: Optional[NotificationService] = None


def get_services():
    """Get or initialize services."""
    global _analyzer, _router, _notifier
    
    if _analyzer is None:
        _analyzer = ComplaintAnalyzer()
    if _router is None:
        _router = ComplaintRouter()
    if _notifier is None:
        _notifier = NotificationService()
    
    return _analyzer, _router, _notifier


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Complaint Location Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "POST /api/complaint": "Submit a complaint and get full analysis",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/api/complaint",
    response_model=ComplaintResponse,
    tags=["Complaints"],
    summary="Submit a complaint",
    description="Submit a complaint and receive complete analysis including location extraction, classification, routing, and notification status"
)
async def submit_complaint(request: ComplaintRequest):
    """
    Submit a complaint and return all outputs from the complete workflow.
    
    This endpoint performs:
    1. Location extraction from the complaint text
    2. Multi-stage classification (LLM + Semantic matching)
    3. Department routing based on classification
    4. Priority calculation
    5. Notification sending (department and optional user confirmation)
    
    Returns:
        Complete response with location data, routing result, and notification status
    """
    try:
        # Get services
        analyzer, router, notifier = get_services()
        
        # Initialize response variables
        location_data = None
        routing_result = None
        notification_status = None
        
        # Step 1: Extract location from complaint
        try:
            location_data_dict = analyzer.analyze_complaint(request.complaint)
            if location_data_dict:
                location_data = LocationData(**location_data_dict)
        except Exception as e:
            # Continue without location data if extraction fails
            location_data_dict = {}
        
        # Step 2: Prepare user info
        user_info_dict = {}
        if request.user_info:
            if request.user_info.name:
                user_info_dict['name'] = request.user_info.name
            if request.user_info.email:
                user_info_dict['email'] = request.user_info.email
            if request.user_info.phone:
                user_info_dict['phone'] = request.user_info.phone
        
        # Step 3: Route complaint (includes classification)
        try:
            routing_result_dict = router.route_complaint(
                complaint=request.complaint,
                location_data=location_data_dict,
                user_info=user_info_dict
            )
            routing_result = RoutingResult(**routing_result_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Routing failed: {str(e)}"
            )
        
        # Step 4: Send notifications
        try:
            department_sent = notifier.send_department_notification(
                routing_result_dict['department']['email'],
                {
                    'ticket_id': routing_result_dict['ticket_id'],
                    'department': routing_result_dict['department'],
                    'priority': routing_result_dict['priority'],
                    'estimated_response_hours': routing_result_dict['estimated_response_hours'],
                    'classification': routing_result_dict['classification'],
                    'location': routing_result_dict['location'],
                    'user_info': routing_result_dict['user_info'],
                    'routed_at': routing_result_dict['routed_at']
                }
            )
            
            user_sent = False
            user_error = None
            if request.user_info and request.user_info.email:
                try:
                    user_sent = notifier.send_user_confirmation(
                        request.user_info.email,
                        {
                            'ticket_id': routing_result_dict['ticket_id'],
                            'department': routing_result_dict['department'],
                            'priority': routing_result_dict['priority'],
                            'estimated_response_hours': routing_result_dict['estimated_response_hours'],
                            'classification': routing_result_dict['classification'],
                            'location': routing_result_dict['location'],
                            'routed_at': routing_result_dict['routed_at']
                        }
                    )
                except Exception as e:
                    user_error = str(e)
            
            notification_status = NotificationStatus(
                department_notification_sent=department_sent,
                user_confirmation_sent=user_sent,
                department_notification_error=None if department_sent else "SMTP not configured",
                user_notification_error=user_error
            )
        except Exception as e:
            notification_status = NotificationStatus(
                department_notification_sent=False,
                user_confirmation_sent=False,
                department_notification_error=str(e),
                user_notification_error=str(e)
            )
        
        # Build success response
        return ComplaintResponse(
            success=True,
            message="Complaint processed successfully",
            timestamp=datetime.now().isoformat(),
            location_data=location_data,
            routing_result=routing_result,
            notification_status=notification_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
