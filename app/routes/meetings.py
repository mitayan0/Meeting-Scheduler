"""API routes for meeting management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingParticipantCreate,
    MeetingParticipantResponse
)
from app.services.meeting_service import MeetingService
from app.services.ics_service import ICSService

router = APIRouter(prefix="/api/meetings", tags=["Meetings"])


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new meeting.
    
    Args:
        meeting_data: Meeting creation data
        db: Database session
        
    Returns:
        Created meeting with participants
    """
    meeting = MeetingService.create_meeting(db, meeting_data)
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "location": meeting.location,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
        "participants": MeetingService.format_meeting_participants(meeting)
    }


@router.get("/", response_model=List[MeetingResponse])
def get_meetings(
    participant_id: Optional[UUID] = Query(None, description="Filter by participant ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """
    Get all meetings with optional filters.
    
    Args:
        participant_id: Optional participant ID to filter by
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        
    Returns:
        List of meetings
    """
    meetings = MeetingService.get_meetings(
        db=db,
        participant_id=participant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    response = []
    for meeting in meetings:
        meeting_dict = {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "location": meeting.location,
            "created_at": meeting.created_at,
            "updated_at": meeting.updated_at,
            "participants": MeetingService.format_meeting_participants(meeting)
        }
        response.append(meeting_dict)
    
    return response


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a meeting by ID.
    
    Args:
        meeting_id: Meeting ID
        db: Database session
        
    Returns:
        Meeting details with participants
    """
    meeting = MeetingService.get_meeting(db, meeting_id)
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "location": meeting.location,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
        "participants": MeetingService.format_meeting_participants(meeting)
    }


@router.put("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: UUID,
    meeting_data: MeetingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a meeting.
    
    Args:
        meeting_id: Meeting ID
        meeting_data: Meeting update data
        db: Database session
        
    Returns:
        Updated meeting
    """
    meeting = MeetingService.update_meeting(db, meeting_id, meeting_data)
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "description": meeting.description,
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "location": meeting.location,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
        "participants": MeetingService.format_meeting_participants(meeting)
    }


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a meeting.
    
    Args:
        meeting_id: Meeting ID
        db: Database session
    """
    MeetingService.delete_meeting(db, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{meeting_id}/participants", response_model=MeetingParticipantResponse, status_code=status.HTTP_201_CREATED)
def add_participant_to_meeting(
    meeting_id: UUID,
    participant_data: MeetingParticipantCreate,
    db: Session = Depends(get_db)
):
    """
    Add a participant to a meeting.
    
    Args:
        meeting_id: Meeting ID
        participant_data: Participant data
        db: Database session
        
    Returns:
        Created meeting participant relationship
    """
    meeting_participant = MeetingService.add_participant_to_meeting(
        db=db,
        meeting_id=meeting_id,
        participant_id=participant_data.participant_id
    )
    
    return meeting_participant


@router.delete("/{meeting_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant_from_meeting(
    meeting_id: UUID,
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove a participant from a meeting.
    
    Args:
        meeting_id: Meeting ID
        participant_id: Participant ID
        db: Database session
    """
    MeetingService.remove_participant_from_meeting(db, meeting_id, participant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{meeting_id}/export")
def export_meeting_as_ics(
    meeting_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Export a meeting as an ICS (iCalendar) file.
    
    Args:
        meeting_id: Meeting ID
        db: Database session
        
    Returns:
        ICS file download
    """
    meeting = MeetingService.get_meeting(db, meeting_id)
    
    # Generate ICS content
    ics_content = ICSService.generate_ics(meeting, meeting.meeting_participants)
    
    # Create safe filename
    safe_title = "".join(c for c in meeting.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_title}.ics"
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
