"""Notification service for simulated notifications."""

import logging
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import MeetingParticipant

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class NotificationService:
    """Service for handling notifications."""
    
    @staticmethod
    def notify_meeting_created(
        db: Session,
        meeting_id: UUID,
        meeting_title: str,
        participant_emails: List[str]
    ) -> None:
        """
        Simulate notification for meeting creation.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            meeting_title: Meeting title
            participant_emails: List of participant emails
        """
        logger.info(
            f"[NOTIFICATION] Meeting Created: '{meeting_title}' (ID: {meeting_id})"
        )
        for email in participant_emails:
            logger.info(f"  → Notifying participant: {email}")
        
        # Update notification timestamp
        NotificationService._update_notification_timestamp(db, meeting_id)
    
    @staticmethod
    def notify_meeting_updated(
        db: Session,
        meeting_id: UUID,
        meeting_title: str,
        participant_emails: List[str]
    ) -> None:
        """
        Simulate notification for meeting update.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            meeting_title: Meeting title
            participant_emails: List of participant emails
        """
        logger.info(
            f"[NOTIFICATION] Meeting Updated: '{meeting_title}' (ID: {meeting_id})"
        )
        for email in participant_emails:
            logger.info(f"  → Notifying participant: {email}")
        
        # Update notification timestamp
        NotificationService._update_notification_timestamp(db, meeting_id)
    
    @staticmethod
    def notify_meeting_cancelled(
        meeting_id: UUID,
        meeting_title: str,
        participant_emails: List[str]
    ) -> None:
        """
        Simulate notification for meeting cancellation.
        
        Args:
            meeting_id: Meeting ID
            meeting_title: Meeting title
            participant_emails: List of participant emails
        """
        logger.info(
            f"[NOTIFICATION] Meeting Cancelled: '{meeting_title}' (ID: {meeting_id})"
        )
        for email in participant_emails:
            logger.info(f"  → Notifying participant: {email}")
    
    @staticmethod
    def notify_participant_added(
        db: Session,
        meeting_id: UUID,
        meeting_title: str,
        participant_email: str
    ) -> None:
        """
        Simulate notification for participant addition.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
            meeting_title: Meeting title
            participant_email: Participant email
        """
        logger.info(
            f"[NOTIFICATION] Participant Added to '{meeting_title}' (ID: {meeting_id})"
        )
        logger.info(f"  → Notifying participant: {participant_email}")
        
        # Update notification timestamp for specific participant
        meeting_participant = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id
        ).join(MeetingParticipant.participant).filter(
            MeetingParticipant.participant.has(email=participant_email)
        ).first()
        
        if meeting_participant:
            meeting_participant.notified_at = datetime.now(timezone.utc)
            db.commit()
    
    @staticmethod
    def _update_notification_timestamp(db: Session, meeting_id: UUID) -> None:
        """
        Update notification timestamp for all participants of a meeting.
        
        Args:
            db: Database session
            meeting_id: Meeting ID
        """
        now = datetime.now(timezone.utc)
        meeting_participants = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id
        ).all()
        
        for mp in meeting_participants:
            mp.notified_at = now
        
        db.commit()
