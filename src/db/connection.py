"""
Database connection management for AI Complaint System.
"""

import sqlite3
from typing import Optional
from pathlib import Path

from src.config.settings import settings


# Global connection variable
_connection: Optional[sqlite3.Connection] = None


def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection.
    
    Returns:
        SQLite database connection
    """
    global _connection
    
    if _connection is None:
        # Parse database URL
        db_url = settings.database_url
        
        if db_url.startswith('sqlite:///'):
            # Extract path from URL
            db_path = db_url.replace('sqlite:///', '')
            
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            _connection = sqlite3.connect(db_path)
            _connection.row_factory = sqlite3.Row  # Enable column access by name
        else:
            raise ValueError(f"Unsupported database URL: {db_url}")
    
    return _connection


def close_db_connection() -> None:
    """Close the database connection if open."""
    global _connection
    
    if _connection is not None:
        _connection.close()
        _connection = None


def init_db() -> None:
    """
    Initialize the database schema.
    Creates all necessary tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            complaint_text TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            urgency TEXT NOT NULL,
            location_data TEXT,
            user_info TEXT,
            department_id TEXT,
            priority TEXT NOT NULL,
            estimated_response_hours INTEGER NOT NULL,
            status TEXT NOT NULL,
            keywords TEXT,
            summary TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            resolved_at TIMESTAMP
        )
    """)
    
    # Create complaint_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_by TEXT,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaints_ticket_id 
        ON complaints(ticket_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaints_status 
        ON complaints(status)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaints_department 
        ON complaints(department_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_complaint_history_complaint_id 
        ON complaint_history(complaint_id)
    """)
    
    conn.commit()
    print("✅ Database initialized successfully!")


def reset_db() -> None:
    """
    Reset the database by dropping all tables.
    WARNING: This will delete all data!
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS complaint_history")
    cursor.execute("DROP TABLE IF EXISTS complaints")
    
    conn.commit()
    print("⚠️  Database reset successfully!")
