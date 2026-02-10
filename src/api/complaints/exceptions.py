"""Domain-specific exceptions for the complaints module."""

from fastapi import HTTPException, status


class ComplaintRoutingError(HTTPException):
    """Exception raised when complaint routing fails."""
    
    def __init__(self, detail: str = "Failed to route complaint"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class ComplaintValidationError(HTTPException):
    """Exception raised when complaint validation fails."""
    
    def __init__(self, detail: str = "Complaint validation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class NotificationError(HTTPException):
    """Exception raised when notification sending fails."""
    
    def __init__(self, detail: str = "Failed to send notification"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
