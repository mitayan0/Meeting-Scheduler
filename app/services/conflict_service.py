"""Conflict detection service."""

from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import Meeting, MeetingParticipant, Participant
from app.schemas import ConflictInfo


class ConflictService:
    """Service for detecting scheduling conflicts."""
    
    @staticmethod
    def check_conflicts(
        db: Session,
        participant_ids: List[UUID],
        start_time: datetime,
        end_time: datetime,
        exclude_meeting_id: UUID = None
    ) -> Tuple[bool, List[ConflictInfo]]:
        """
        Check for scheduling conflicts for given participants and time slot.
        
        Args:
            db: Database session
            participant_ids: List of participant UUIDs
            start_time: Start time of the proposed meeting
            end_time: End time of the proposed meeting
            exclude_meeting_id: Optional meeting ID to exclude from conflict check
            
        Returns:
            Tuple of (has_conflicts: bool, conflicts: List[ConflictInfo])
        """
        conflicts = []
        
        for participant_id in participant_ids:
            # Get participant
            participant = db.query(Participant).filter(
                Participant.id == participant_id
            ).first()
            
            if not participant:
                continue
            
            # Find overlapping meetings for this participant
            query = db.query(Meeting).join(
                MeetingParticipant,
                Meeting.id == MeetingParticipant.meeting_id
            ).filter(
                MeetingParticipant.participant_id == participant_id,
                or_(
                    # Case 1: Existing meeting starts during the proposed time
                    and_(
                        Meeting.start_time >= start_time,
                        Meeting.start_time < end_time
                    ),
                    # Case 2: Existing meeting ends during the proposed time
                    and_(
                        Meeting.end_time > start_time,
                        Meeting.end_time <= end_time
                    ),
                    # Case 3: Existing meeting completely encompasses the proposed time
                    and_(
                        Meeting.start_time <= start_time,
                        Meeting.end_time >= end_time
                    )
                )
            )
            
            # Exclude specific meeting if provided
            if exclude_meeting_id:
                query = query.filter(Meeting.id != exclude_meeting_id)
            
            conflicting_meetings = query.all()
            
            # Add conflicts to list
            for meeting in conflicting_meetings:
                conflict = ConflictInfo(
                    participant_id=participant.id,
                    participant_name=participant.name,
                    participant_email=participant.email,
                    conflicting_meeting_id=meeting.id,
                    conflicting_meeting_title=meeting.title,
                    conflicting_start_time=meeting.start_time,
                    conflicting_end_time=meeting.end_time
                )
                conflicts.append(conflict)
        
        has_conflicts = len(conflicts) > 0
        return has_conflicts, conflicts
