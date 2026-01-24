"""
Complaint data model and status workflow.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import json


class ComplaintStatus(Enum):
    """Complaint status workflow."""
    SUBMITTED = "submitted"
    ROUTED = "routed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Complaint:
    """
    Complaint model with full lifecycle tracking.
    """
    
    def __init__(
        self,
        ticket_id: str,
        complaint_text: str,
        category: str,
        severity: str,
        urgency: str,
        location_data: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, str]] = None,
        department_id: Optional[str] = None,
        priority: str = "medium",
        estimated_response_hours: int = 48,
        status: ComplaintStatus = ComplaintStatus.SUBMITTED,
        keywords: Optional[List[str]] = None,
        summary: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        """
        Initialize a Complaint instance.
        
        Args:
            ticket_id: Unique ticket identifier
            complaint_text: Original complaint text
            category: Complaint category
            severity: Severity level (low, medium, high, critical)
            urgency: Urgency level (routine, urgent, emergency)
            location_data: Location information (lat, lng, formatted_address, place_name)
            user_info: User information (name, email, phone)
            department_id: Assigned department ID
            priority: Overall priority level
            estimated_response_hours: Expected response time in hours
            status: Current complaint status
            keywords: Extracted keywords
            summary: Complaint summary
            created_at: Creation timestamp
            updated_at: Last update timestamp
            resolved_at: Resolution timestamp
            id: Database ID (if saved)
        """
        self.id = id
        self.ticket_id = ticket_id
        self.complaint_text = complaint_text
        self.category = category
        self.severity = severity
        self.urgency = urgency
        self.location_data = location_data or {}
        self.user_info = user_info or {}
        self.department_id = department_id
        self.priority = priority
        self.estimated_response_hours = estimated_response_hours
        self.status = status
        self.keywords = keywords or []
        self.summary = summary or complaint_text[:100]
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.resolved_at = resolved_at
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert complaint to dictionary.
        
        Returns:
            Dictionary representation of the complaint
        """
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'complaint_text': self.complaint_text,
            'category': self.category,
            'severity': self.severity,
            'urgency': self.urgency,
            'location_data': self.location_data,
            'user_info': self.user_info,
            'department_id': self.department_id,
            'priority': self.priority,
            'estimated_response_hours': self.estimated_response_hours,
            'status': self.status.value,
            'keywords': self.keywords,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Complaint':
        """
        Create Complaint from dictionary.
        
        Args:
            data: Dictionary with complaint data
            
        Returns:
            Complaint instance
        """
        # Parse datetime strings
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        resolved_at = datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None
        
        # Parse status
        status = ComplaintStatus(data.get('status', 'submitted'))
        
        return cls(
            id=data.get('id'),
            ticket_id=data['ticket_id'],
            complaint_text=data['complaint_text'],
            category=data['category'],
            severity=data['severity'],
            urgency=data['urgency'],
            location_data=data.get('location_data', {}),
            user_info=data.get('user_info', {}),
            department_id=data.get('department_id'),
            priority=data.get('priority', 'medium'),
            estimated_response_hours=data.get('estimated_response_hours', 48),
            status=status,
            keywords=data.get('keywords', []),
            summary=data.get('summary'),
            created_at=created_at,
            updated_at=updated_at,
            resolved_at=resolved_at,
        )
    
    def update_status(self, new_status: ComplaintStatus, notes: Optional[str] = None) -> None:
        """
        Update complaint status.
        
        Args:
            new_status: New status to set
            notes: Optional notes about the status change
        """
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == ComplaintStatus.RESOLVED:
            self.resolved_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """
        Check if complaint is overdue based on estimated response time.
        
        Returns:
            True if overdue, False otherwise
        """
        if not self.created_at:
            return False
        
        elapsed_hours = (datetime.now() - self.created_at).total_seconds() / 3600
        return elapsed_hours > self.estimated_response_hours and self.status not in [
            ComplaintStatus.RESOLVED,
            ComplaintStatus.CLOSED
        ]
    
    def get_age_hours(self) -> float:
        """
        Get complaint age in hours.
        
        Returns:
            Age in hours
        """
        if not self.created_at:
            return 0.0
        
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    def get_location_display(self) -> str:
        """
        Get formatted location display string.
        
        Returns:
            Location display string
        """
        if not self.location_data:
            return "Not specified"
        
        return self.location_data.get('formatted_address') or self.location_data.get('place_name', 'Not specified')
    
    def get_user_display(self) -> str:
        """
        Get formatted user display string.
        
        Returns:
            User display string
        """
        if not self.user_info:
            return "Anonymous"
        
        name = self.user_info.get('name', 'Anonymous')
        email = self.user_info.get('email', '')
        
        if email:
            return f"{name} ({email})"
        return name
    
    def __repr__(self) -> str:
        """String representation of the complaint."""
        return f"<Complaint(id={self.id}, ticket_id={self.ticket_id}, status={self.status.value})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"[{self.ticket_id}] {self.category.title()} - {self.status.value}"


class ComplaintHistory:
    """
    History entry for tracking complaint status changes.
    """
    
    def __init__(
        self,
        complaint_id: int,
        status: ComplaintStatus,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        """
        Initialize a ComplaintHistory entry.
        
        Args:
            complaint_id: ID of the associated complaint
            status: Status at this point in time
            notes: Optional notes about the change
            created_by: Who made this change
            created_at: When this change was made
            id: Database ID (if saved)
        """
        self.id = id
        self.complaint_id = complaint_id
        self.status = status
        self.notes = notes
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert history entry to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'status': self.status.value,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComplaintHistory':
        """
        Create ComplaintHistory from dictionary.
        
        Args:
            data: Dictionary with history data
            
        Returns:
            ComplaintHistory instance
        """
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        status = ComplaintStatus(data.get('status', 'submitted'))
        
        return cls(
            id=data.get('id'),
            complaint_id=data['complaint_id'],
            status=status,
            notes=data.get('notes'),
            created_by=data.get('created_by'),
            created_at=created_at,
        )
