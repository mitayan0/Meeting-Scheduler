"""Utility functions for the application."""

import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a new UUID as string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime_for_ics(dt: datetime) -> str:
    """
    Format datetime for ICS file.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted string in ICS format (YYYYMMDDTHHMMSSZ)
    """
    return dt.strftime("%Y%m%dT%H%M%SZ")
