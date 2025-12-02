"""API routes for participant management."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Participant
from app.schemas import ParticipantCreate, ParticipantResponse, MeetingResponse
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/api/participants", tags=["Participants"])


@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_participant(
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new participant.
    
    Args:
        participant_data: Participant creation data
        db: Database session
        
    Returns:
        Created participant
    """
    # Check if email already exists
    existing = db.query(Participant).filter(
        Participant.email == participant_data.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant with this email already exists"
        )
    
    participant = Participant(
        name=participant_data.name,
        email=participant_data.email
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    return participant


@router.get("/", response_model=List[ParticipantResponse])
def get_participants(db: Session = Depends(get_db)):
    """
    Get all participants.
    
    Args:
        db: Database session
        
    Returns:
        List of participants
    """
    participants = db.query(Participant).all()
    return participants


@router.get("/{participant_id}", response_model=ParticipantResponse)
def get_participant(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a participant by ID.
    
    Args:
        participant_id: Participant ID
        db: Database session
        
    Returns:
        Participant details
    """
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with id {participant_id} not found"
        )
    
    return participant


@router.get("/{participant_id}/meetings", response_model=List[MeetingResponse])
def get_participant_meetings(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all meetings for a participant.
    
    Args:
        participant_id: Participant ID
        db: Database session
        
    Returns:
        List of meetings
    """
    # Verify participant exists
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant with id {participant_id} not found"
        )
    
    meetings = MeetingService.get_meetings(db, participant_id=participant_id)
    
    # Format response
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
