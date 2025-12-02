"""Meeting service for business logic."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models import Meeting, Participant, MeetingParticipant
from app.schemas import MeetingCreate, MeetingUpdate, MeetingParticipantInfo
from app.services.notification_service import NotificationService


class MeetingService:
    """Service for meeting-related business logic."""
    
    @staticmethod
    def create_meeting(db: Session, meeting_data: MeetingCreate) -> Meeting:
        """
        Create a new meeting.
        
        Args:
            db: Database session
            meeting_data: Meeting creation data
            
        Returns:
            Created Meeting object
        """
        # Create meeting
        meeting = Meeting(
            title=meeting_data.title,
            description=meeting_data.description,
            start_time=meeting_data.start_time,
            end_time=meeting_data.end_time,
            location=meeting_data.location
        )
        
        db.add(meeting)
        db.flush()  # Flush to get the meeting ID
        
        # Add participants if provided
        participant_emails = []
        if meeting_data.participant_ids:
            for participant_id in meeting_data.participant_ids:
                participant = db.query(Participant).filter(
                    Participant.id == participant_id
                ).first()
                
                if not participant:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Participant with id {participant_id} not found"
                    )
                
                meeting_participant = MeetingParticipant(
                    meeting_id=meeting.id,
                    participant_id=participant_id
                )
                db.add(meeting_participant)
                participant_emails.append(participant.email)
        
        db.commit()
        db.refresh(meeting)
        
        # Send notifications
        if participant_emails:
            NotificationService.notify_meeting_created(
                db, meeting.id, meeting.title, participant_emails
            )
        
        return meeting
    
    @staticmethod
    def get_meeting(db: Session, meeting_id: UUID) -> Meeting:
        """
        Get a meeting by ID.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            
        Returns:
            Meeting object
        """
        meeting = db.query(Meeting).options(
            joinedload(Meeting.meeting_participants).joinedload(MeetingParticipant.participant)
        ).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with id {meeting_id} not found"
            )
        
        return meeting
    
    @staticmethod
    def get_meetings(
        db: Session,
        participant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Meeting]:
        """
        Get meetings with optional filters.
        
        Args:
            db: Database session
            participant_id: Optional participant ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of Meeting objects
        """
        query = db.query(Meeting).options(
            joinedload(Meeting.meeting_participants).joinedload(MeetingParticipant.participant)
        )
        
        # Filter by participant
        if participant_id:
            query = query.join(MeetingParticipant).filter(
                MeetingParticipant.participant_id == participant_id
            )
        
        # Filter by date range
        if start_date:
            query = query.filter(Meeting.start_time >= start_date)
        if end_date:
            query = query.filter(Meeting.end_time <= end_date)
        
        return query.all()
    
    @staticmethod
    def update_meeting(
        db: Session,
        meeting_id: UUID,
        meeting_data: MeetingUpdate
    ) -> Meeting:
        """
        Update a meeting.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            meeting_data: Meeting update data
            
        Returns:
            Updated Meeting object
        """
        meeting = MeetingService.get_meeting(db, meeting_id)
        
        # Update fields if provided
        update_data = meeting_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        
        db.commit()
        db.refresh(meeting)
        
        # Send notifications
        participant_emails = [
            mp.participant.email for mp in meeting.meeting_participants
        ]
        if participant_emails:
            NotificationService.notify_meeting_updated(
                db, meeting.id, meeting.title, participant_emails
            )
        
        return meeting
    
    @staticmethod
    def delete_meeting(db: Session, meeting_id: UUID) -> None:
        """
        Delete a meeting.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
        """
        meeting = MeetingService.get_meeting(db, meeting_id)
        
        # Get participant emails before deletion
        participant_emails = [
            mp.participant.email for mp in meeting.meeting_participants
        ]
        meeting_title = meeting.title
        
        db.delete(meeting)
        db.commit()
        
        # Send cancellation notifications
        if participant_emails:
            NotificationService.notify_meeting_cancelled(
                meeting_id, meeting_title, participant_emails
            )
    
    @staticmethod
    def add_participant_to_meeting(
        db: Session,
        meeting_id: UUID,
        participant_id: UUID
    ) -> MeetingParticipant:
        """
        Add a participant to a meeting.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            participant_id: Participant ID
            
        Returns:
            Created MeetingParticipant object
        """
        # Verify meeting exists
        meeting = MeetingService.get_meeting(db, meeting_id)
        
        # Verify participant exists
        participant = db.query(Participant).filter(
            Participant.id == participant_id
        ).first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with id {participant_id} not found"
            )
        
        # Check if already added
        existing = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.participant_id == participant_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Participant already added to this meeting"
            )
        
        # Add participant
        meeting_participant = MeetingParticipant(
            meeting_id=meeting_id,
            participant_id=participant_id
        )
        
        db.add(meeting_participant)
        db.commit()
        db.refresh(meeting_participant)
        
        # Send notification
        NotificationService.notify_participant_added(
            db, meeting_id, meeting.title, participant.email
        )
        
        return meeting_participant
    
    @staticmethod
    def remove_participant_from_meeting(
        db: Session,
        meeting_id: UUID,
        participant_id: UUID
    ) -> None:
        """
        Remove a participant from a meeting.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            participant_id: Participant ID
        """
        meeting_participant = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.participant_id == participant_id
        ).first()
        
        if not meeting_participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found in this meeting"
            )
        
        db.delete(meeting_participant)
        db.commit()
    
    @staticmethod
    def format_meeting_participants(
        meeting: Meeting
    ) -> List[MeetingParticipantInfo]:
        """
        Format meeting participants for response.
        
        Args:
            meeting: Meeting object
            
        Returns:
            List of MeetingParticipantInfo
        """
        return [
            MeetingParticipantInfo(
                id=mp.id,
                participant_id=mp.participant.id,
                name=mp.participant.name,
                email=mp.participant.email,
                status=mp.status,
                notified_at=mp.notified_at
            )
            for mp in meeting.meeting_participants
        ]
