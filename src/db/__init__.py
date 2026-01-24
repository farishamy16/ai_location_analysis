"""
Database module for AI Complaint System.
"""

from .connection import get_db_connection, init_db
from .repositories import ComplaintRepository, ComplaintHistoryRepository

__all__ = [
    'get_db_connection',
    'init_db',
    'ComplaintRepository',
    'ComplaintHistoryRepository',
]
