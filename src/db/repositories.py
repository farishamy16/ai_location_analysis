"""
Data access layer for complaints and history.
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.db.connection import get_db_connection
from src.models.complaint import Complaint, ComplaintHistory, ComplaintStatus


class ComplaintRepository:
    """Repository for complaint data access."""
    
    @staticmethod
    def create(complaint: Complaint) -> Complaint:
        """
        Create a new complaint in the database.
        
        Args:
            complaint: Complaint object to create
            
        Returns:
            Created complaint with ID assigned
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO complaints (
                ticket_id, complaint_text, category, severity, urgency,
                location_data, user_info, department_id, priority,
                estimated_response_hours, status, keywords, summary,
                created_at, updated_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint.ticket_id,
            complaint.complaint_text,
            complaint.category,
            complaint.severity,
            complaint.urgency,
            json.dumps(complaint.location_data),
            json.dumps(complaint.user_info),
            complaint.department_id,
            complaint.priority,
            complaint.estimated_response_hours,
            complaint.status.value,
            json.dumps(complaint.keywords),
            complaint.summary,
            complaint.created_at.isoformat(),
            complaint.updated_at.isoformat(),
            complaint.resolved_at.isoformat() if complaint.resolved_at else None
        ))
        
        conn.commit()
        complaint.id = cursor.lastrowid
        
        return complaint
    
    @staticmethod
    def get_by_id(complaint_id: int) -> Optional[Complaint]:
        """
        Get a complaint by database ID.
        
        Args:
            complaint_id: Database ID
            
        Returns:
            Complaint object or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
        row = cursor.fetchone()
        
        if row:
            return ComplaintRepository._row_to_complaint(row)
        return None
    
    @staticmethod
    def get_by_ticket_id(ticket_id: str) -> Optional[Complaint]:
        """
        Get a complaint by ticket ID.
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Complaint object or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        
        if row:
            return ComplaintRepository._row_to_complaint(row)
        return None
    
    @staticmethod
    def get_all(limit: Optional[int] = None, status: Optional[str] = None) -> List[Complaint]:
        """
        Get all complaints, optionally filtered.
        
        Args:
            limit: Maximum number of complaints to return
            status: Filter by status
            
        Returns:
            List of Complaint objects
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM complaints"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [ComplaintRepository._row_to_complaint(row) for row in rows]
    
    @staticmethod
    def update(complaint: Complaint) -> Complaint:
        """
        Update an existing complaint.
        
        Args:
            complaint: Complaint object with updated data
            
        Returns:
            Updated complaint
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE complaints SET
                complaint_text = ?,
                category = ?,
                severity = ?,
                urgency = ?,
                location_data = ?,
                user_info = ?,
                department_id = ?,
                priority = ?,
                estimated_response_hours = ?,
                status = ?,
                keywords = ?,
                summary = ?,
                updated_at = ?,
                resolved_at = ?
            WHERE id = ?
        """, (
            complaint.complaint_text,
            complaint.category,
            complaint.severity,
            complaint.urgency,
            json.dumps(complaint.location_data),
            json.dumps(complaint.user_info),
            complaint.department_id,
            complaint.priority,
            complaint.estimated_response_hours,
            complaint.status.value,
            json.dumps(complaint.keywords),
            complaint.summary,
            complaint.updated_at.isoformat(),
            complaint.resolved_at.isoformat() if complaint.resolved_at else None,
            complaint.id
        ))
        
        conn.commit()
        
        return complaint
    
    @staticmethod
    def update_status(complaint_id: int, new_status: ComplaintStatus, notes: Optional[str] = None) -> None:
        """
        Update complaint status.
        
        Args:
            complaint_id: Database ID of complaint
            new_status: New status to set
            notes: Optional notes about the change
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update complaint
        updated_at = datetime.now()
        resolved_at = updated_at if new_status == ComplaintStatus.RESOLVED else None
        
        cursor.execute("""
            UPDATE complaints SET
                status = ?,
                updated_at = ?,
                resolved_at = ?
            WHERE id = ?
        """, (new_status.value, updated_at.isoformat(), resolved_at.isoformat() if resolved_at else None, complaint_id))
        
        conn.commit()
    
    @staticmethod
    def delete(complaint_id: int) -> bool:
        """
        Delete a complaint.
        
        Args:
            complaint_id: Database ID of complaint
            
        Returns:
            True if deleted, False if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
        conn.commit()
        
        return cursor.rowcount > 0
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        Get complaint statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total complaints
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM complaints 
            GROUP BY status
        """)
        by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # By category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM complaints 
            GROUP BY category
        """)
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # By severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM complaints 
            GROUP BY severity
        """)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total': total,
            'by_status': by_status,
            'by_category': by_category,
            'by_severity': by_severity
        }
    
    @staticmethod
    def _row_to_complaint(row: Dict[str, Any]) -> Complaint:
        """
        Convert database row to Complaint object.
        
        Args:
            row: Database row
            
        Returns:
            Complaint object
        """
        return Complaint(
            id=row['id'],
            ticket_id=row['ticket_id'],
            complaint_text=row['complaint_text'],
            category=row['category'],
            severity=row['severity'],
            urgency=row['urgency'],
            location_data=json.loads(row['location_data']) if row['location_data'] else {},
            user_info=json.loads(row['user_info']) if row['user_info'] else {},
            department_id=row['department_id'],
            priority=row['priority'],
            estimated_response_hours=row['estimated_response_hours'],
            status=ComplaintStatus(row['status']),
            keywords=json.loads(row['keywords']) if row['keywords'] else [],
            summary=row['summary'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
        )


class ComplaintHistoryRepository:
    """Repository for complaint history data access."""
    
    @staticmethod
    def create(history: ComplaintHistory) -> ComplaintHistory:
        """
        Create a new history entry.
        
        Args:
            history: ComplaintHistory object to create
            
        Returns:
            Created history with ID assigned
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO complaint_history (
                complaint_id, status, notes, created_by, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            history.complaint_id,
            history.status.value,
            history.notes,
            history.created_by,
            history.created_at.isoformat()
        ))
        
        conn.commit()
        history.id = cursor.lastrowid
        
        return history
    
    @staticmethod
    def get_by_complaint_id(complaint_id: int) -> List[ComplaintHistory]:
        """
        Get all history entries for a complaint.
        
        Args:
            complaint_id: Database ID of complaint
            
        Returns:
            List of ComplaintHistory objects
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM complaint_history 
            WHERE complaint_id = ? 
            ORDER BY created_at ASC
        """, (complaint_id,))
        
        rows = cursor.fetchall()
        
        return [ComplaintHistoryRepository._row_to_history(row) for row in rows]
    
    @staticmethod
    def _row_to_history(row: Dict[str, Any]) -> ComplaintHistory:
        """
        Convert database row to ComplaintHistory object.
        
        Args:
            row: Database row
            
        Returns:
            ComplaintHistory object
        """
        return ComplaintHistory(
            id=row['id'],
            complaint_id=row['complaint_id'],
            status=ComplaintStatus(row['status']),
            notes=row['notes'],
            created_by=row['created_by'],
            created_at=datetime.fromisoformat(row['created_at']),
        )
