"""
Notification Service
Handles email notifications for complaints.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from pathlib import Path

from src.config.settings import settings


class NotificationService:
    """Service for sending email notifications."""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        """
        Initialize the notification service.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            from_email: From email address
            from_name: From name
        """
        self.smtp_server = smtp_server or settings.smtp_server
        self.smtp_port = smtp_port or settings.smtp_port
        self.smtp_username = smtp_username or settings.smtp_username
        self.smtp_password = smtp_password or settings.smtp_password
        self.from_email = from_email or settings.from_email
        self.from_name = from_name or settings.from_name
    
    def send_department_notification(
        self,
        to_email: str,
        complaint_data: Dict[str, Any]
    ) -> bool:
        """
        Send email notification to department about a new complaint.
        
        Args:
            to_email: Recipient email address
            complaint_data: Dictionary with complaint and routing information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"New Complaint: {complaint_data['ticket_id']} - {complaint_data['classification']['category'].title()}"
        
        body = self._format_department_email(complaint_data)
        
        return self._send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=False
        )
    
    def send_user_confirmation(
        self,
        to_email: str,
        complaint_data: Dict[str, Any]
    ) -> bool:
        """
        Send confirmation email to user about their complaint.
        
        Args:
            to_email: Recipient email address
            complaint_data: Dictionary with complaint and routing information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Complaint Received: {complaint_data['ticket_id']}"
        
        body = self._format_user_confirmation_email(complaint_data)
        
        return self._send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=False
        )
    
    def _format_department_email(self, complaint_data: Dict[str, Any]) -> str:
        """
        Format email body for department notification.
        
        Args:
            complaint_data: Dictionary with complaint and routing information
            
        Returns:
            Formatted email body
        """
        ticket_id = complaint_data['ticket_id']
        department = complaint_data['department']
        classification = complaint_data['classification']
        location = complaint_data.get('location', {})
        user_info = complaint_data.get('user_info', {})
        
        location_str = location.get('formatted_address', location.get('place_name', 'Not specified'))
        if location.get('lat') and location.get('lng'):
            location_str += f"\nCoordinates: {location['lat']}, {location['lng']}"
        
        body = f"""
NEW COMPLAINT NOTIFICATION
{'=' * 60}

Ticket ID: {ticket_id}
Department: {department['name']}
Priority: {complaint_data['priority'].upper()}
Estimated Response: {complaint_data['estimated_response_hours']} hours

COMPLAINT DETAILS
{'=' * 60}

Category: {classification['category'].title()}
Severity: {classification['severity'].title()}
Urgency: {classification['urgency'].title()}

Summary:
{classification['summary']}

Keywords:
{', '.join(classification.get('keywords', ['N/A']))}

LOCATION
{'=' * 60}

{location_str}

USER INFORMATION
{'=' * 60}

Name: {user_info.get('name', 'Not provided')}
Email: {user_info.get('email', 'Not provided')}
Phone: {user_info.get('phone', 'Not provided')}

ROUTING INFORMATION
{'=' * 60}

Routed At: {complaint_data['routed_at']}
Department Email: {department['email']}
Department Phone: {department['phone']}

---
This is an automated message from AI Complaint System.
Please do not reply to this email.
"""
        return body
    
    def _format_user_confirmation_email(self, complaint_data: Dict[str, Any]) -> str:
        """
        Format email body for user confirmation.
        
        Args:
            complaint_data: Dictionary with complaint and routing information
            
        Returns:
            Formatted email body
        """
        ticket_id = complaint_data['ticket_id']
        department = complaint_data['department']
        classification = complaint_data['classification']
        location = complaint_data.get('location', {})
        
        location_str = location.get('formatted_address', location.get('place_name', 'Not specified'))
        
        body = f"""
COMPLAINT RECEIVED - CONFIRMATION
{'=' * 60}

Thank you for your feedback. Your complaint has been received and
is being processed.

TICKET INFORMATION
{'=' * 60}

Ticket ID: {ticket_id}
Status: Submitted
Priority: {complaint_data['priority'].title()}
Expected Response: {complaint_data['estimated_response_hours']} hours

COMPLAINT DETAILS
{'=' * 60}

Category: {classification['category'].title()}
Severity: {classification['severity'].title()}

Summary:
{classification['summary']}

Location:
{location_str}

ASSIGNED DEPARTMENT
{'=' * 60}

Department: {department['name']}
Email: {department['email']}
Phone: {department['phone']}

WHAT HAPPENS NEXT?
{'=' * 60}

1. Your complaint has been routed to the appropriate department.
2. The department will review your complaint within the expected response time.
3. You may be contacted for additional information if needed.
4. Use your Ticket ID ({ticket_id}) to track the status of your complaint.

TRACKING YOUR COMPLAINT
{'=' * 60}

To track the status of your complaint, please visit:
https://yourapp.com/track/{ticket_id}

Or contact us at support@yourapp.com with your Ticket ID.

---
Thank you for helping improve our community!

AI Complaint System
"""
        return body
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            is_html: Whether the body is HTML
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Check if email sending is enabled
            if not self.smtp_server or not self.smtp_username or not self.smtp_password:
                # Log that email would be sent (for testing without SMTP)
                print(f"📧 Email queued for {to_email} (SMTP not configured)")
                return True
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)  # type: ignore
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False


# Create a default notification service instance for convenience
default_notifier = NotificationService()


def send_department_notification(
    to_email: str,
    complaint_data: Dict[str, Any]
) -> bool:
    """
    Convenience function to send department notification using default service.
    
    Args:
        to_email: Recipient email address
        complaint_data: Dictionary with complaint and routing information
        
    Returns:
        True if email sent successfully, False otherwise
    """
    return default_notifier.send_department_notification(to_email, complaint_data)


def send_user_confirmation(
    to_email: str,
    complaint_data: Dict[str, Any]
) -> bool:
    """
    Convenience function to send user confirmation using default service.
    
    Args:
        to_email: Recipient email address
        complaint_data: Dictionary with complaint and routing information
        
    Returns:
        True if email sent successfully, False otherwise
    """
    return default_notifier.send_user_confirmation(to_email, complaint_data)
