"""SQLAlchemy database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ParticipantStatus(str, enum.Enum):
    """Enum for participant status."""
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class Meeting(Base):
    """Meeting model."""
    
    __tablename__ = "meetings"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    meeting_participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title='{self.title}')>"


class Participant(Base):
    """Participant model."""
    
    __tablename__ = "participants"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    meeting_participants = relationship("MeetingParticipant", back_populates="participant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Participant(id={self.id}, name='{self.name}', email='{self.email}')>"


class MeetingParticipant(Base):
    """Meeting-Participant junction table."""
    
    __tablename__ = "meeting_participants"
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(Uuid(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Uuid(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ParticipantStatus), default=ParticipantStatus.pending, nullable=False)
    notified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('meeting_id', 'participant_id', name='uq_meeting_participant'),
    )
    
    # Relationships
    meeting = relationship("Meeting", back_populates="meeting_participants")
    participant = relationship("Participant", back_populates="meeting_participants")
    
    def __repr__(self):
        return f"<MeetingParticipant(meeting_id={self.meeting_id}, participant_id={self.participant_id}, status={self.status})>"
