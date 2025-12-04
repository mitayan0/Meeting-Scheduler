"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator

from app.models import ParticipantStatus


# Participant Schemas
class ParticipantBase(BaseModel):
    """Base participant schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant."""
    pass


class ParticipantUpdate(BaseModel):
    """Schema for updating a participant."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None



class ParticipantResponse(ParticipantBase):
    """Schema for participant response."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Meeting Schemas
class MeetingBase(BaseModel):
    """Base meeting schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = Field(None, max_length=255)
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class MeetingCreate(MeetingBase):
    """Schema for creating a meeting."""
    participant_ids: Optional[List[UUID]] = Field(default_factory=list)


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time if both are provided."""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class MeetingParticipantInfo(BaseModel):
    """Schema for meeting participant information."""
    id: UUID
    participant_id: UUID
    name: str
    email: EmailStr
    status: ParticipantStatus
    notified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MeetingResponse(MeetingBase):
    """Schema for meeting response."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    participants: List[MeetingParticipantInfo] = []
    
    class Config:
        from_attributes = True


# Meeting Participant Schemas
class MeetingParticipantCreate(BaseModel):
    """Schema for adding a participant to a meeting."""
    participant_id: UUID


class MeetingParticipantResponse(BaseModel):
    """Schema for meeting participant response."""
    id: UUID
    meeting_id: UUID
    participant_id: UUID
    status: ParticipantStatus
    notified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Conflict Check Schema
class ConflictCheckRequest(BaseModel):
    """Schema for conflict check request."""
    participant_ids: List[UUID] = Field(..., min_items=1)
    start_time: datetime
    end_time: datetime
    exclude_meeting_id: Optional[UUID] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Validate that end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class ConflictInfo(BaseModel):
    """Schema for conflict information."""
    participant_id: UUID
    participant_name: str
    participant_email: EmailStr
    conflicting_meeting_id: UUID
    conflicting_meeting_title: str
    conflicting_start_time: datetime
    conflicting_end_time: datetime


class ConflictCheckResponse(BaseModel):
    """Schema for conflict check response."""
    has_conflicts: bool
    conflicts: List[ConflictInfo] = []
