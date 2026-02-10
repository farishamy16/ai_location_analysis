"""Router for the complaints domain."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from src.api.complaints import dependencies, constants, exceptions
from src.api.complaints.schemas import (
    ComplaintRequest,
    ComplaintResponse,
    LocationData,
    RoutingResult,
    NotificationStatus,
    ErrorResponse,
)

router = APIRouter()


@router.post(
    "/complaint",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    description="Submit a complaint and receive complete analysis including location extraction, classification, routing, and notification status",
    tags=[constants.TAG_COMPLAINTS],
    responses={
        status.HTTP_200_OK: {"model": ComplaintResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
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
        extractor, router_service, notifier = dependencies.get_services()
        
        # Initialize response variables
        location_data = None
        routing_result = None
        notification_status = None
        
        # Step 1: Extract location from complaint
        try:
            location_data_dict = extractor.extract_location(request.complaint)
            if location_data_dict:
                # Remove raw data to reduce response size
                location_data_dict.pop('raw', None)
                location_data = LocationData(**location_data_dict)
        except Exception:
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
            routing_result_dict = router_service.route_complaint(
                complaint=request.complaint,
                location_data=location_data_dict,
                user_info=user_info_dict
            )
            # Remove location from routing result to avoid duplication
            routing_result_dict.pop('location', None)
            routing_result = RoutingResult(**routing_result_dict)
        except Exception as e:
            raise exceptions.ComplaintRoutingError(
                detail=f"{constants.ERROR_ROUTING_FAILED}: {str(e)}"
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
                    'location': location_data_dict,
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
                            'location': location_data_dict,
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
            message=constants.SUCCESS_COMPLAINT_PROCESSED,
            timestamp=datetime.now().isoformat(),
            location_data=location_data,
            routing_result=routing_result,
            notification_status=notification_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{constants.ERROR_INTERNAL_SERVER}: {str(e)}"
        )
