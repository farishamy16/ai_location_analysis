"""Route dependencies for the complaints domain."""

from typing import Optional

from src.orchestrators.location_extractor import LocationExtractor
from src.orchestrators.router import ComplaintRouter
from src.services.notifier import NotificationService


# Global service instances (lazy initialization)
_extractor: Optional[LocationExtractor] = None
_router: Optional[ComplaintRouter] = None
_notifier: Optional[NotificationService] = None


def get_services() -> tuple[LocationExtractor, ComplaintRouter, NotificationService]:
    """
    Get or initialize services.
    
    Returns:
        Tuple of (extractor, router, notifier) services
    """
    global _extractor, _router, _notifier
    
    if _extractor is None:
        _extractor = LocationExtractor()
    if _router is None:
        _router = ComplaintRouter()
    if _notifier is None:
        _notifier = NotificationService()
    
    return _extractor, _router, _notifier
