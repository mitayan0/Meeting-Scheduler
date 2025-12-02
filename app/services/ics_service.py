"""ICS (iCalendar) file generation service."""

from datetime import datetime
from typing import List
from icalendar import Calendar, Event
from uuid import UUID

from app.models import Meeting, MeetingParticipant


class ICSService:
    """Service for generating ICS files."""
    
    @staticmethod
    def generate_ics(meeting: Meeting, participants: List[MeetingParticipant]) -> bytes:
        """
        Generate ICS file content for a meeting.
        
        Args:
            meeting: Meeting object
            participants: List of MeetingParticipant objects
            
        Returns:
            ICS file content as bytes
        """
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Meeting Scheduler//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'REQUEST')
        
        # Create event
        event = Event()
        event.add('uid', f'{meeting.id}@meeting-scheduler.com')
        event.add('dtstamp', datetime.utcnow())
        event.add('dtstart', meeting.start_time)
        event.add('dtend', meeting.end_time)
        event.add('summary', meeting.title)
        
        if meeting.description:
            event.add('description', meeting.description)
        
        if meeting.location:
            event.add('location', meeting.location)
        
        # Add organizer (using first participant as organizer, or empty if no participants)
        if participants:
            organizer_participant = participants[0].participant
            event.add('organizer', f'mailto:{organizer_participant.email}')
            event.add('organizer', organizer_participant.name, parameters={'CN': organizer_participant.name})
        
        # Add attendees
        for mp in participants:
            participant = mp.participant
            event.add('attendee', f'mailto:{participant.email}', parameters={
                'CN': participant.name,
                'ROLE': 'REQ-PARTICIPANT',
                'PARTSTAT': ICSService._get_partstat(mp.status.value),
                'RSVP': 'TRUE'
            })
        
        # Add event to calendar
        cal.add_component(event)
        
        # Return ICS content
        return cal.to_ical()
    
    @staticmethod
    def _get_partstat(status: str) -> str:
        """
        Convert internal status to iCalendar PARTSTAT.
        
        Args:
            status: Internal status (pending, accepted, declined)
            
        Returns:
            iCalendar PARTSTAT value
        """
        status_mapping = {
            'pending': 'NEEDS-ACTION',
            'accepted': 'ACCEPTED',
            'declined': 'DECLINED'
        }
        return status_mapping.get(status, 'NEEDS-ACTION')
