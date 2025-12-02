"""Tests for meeting endpoints."""

from datetime import datetime, timezone, timedelta
import pytest


class TestMeetingCreation:
    """Test meeting creation."""
    
    def test_create_meeting_success(self, client, sample_participant):
        """Test successful meeting creation."""
        meeting_data = {
            "title": "Team Standup",
            "description": "Daily team standup meeting",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).isoformat(),
            "location": "Conference Room A",
            "participant_ids": [str(sample_participant.id)]
        }
        
        response = client.post("/api/meetings/", json=meeting_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Team Standup"
        assert data["description"] == "Daily team standup meeting"
        assert data["location"] == "Conference Room A"
        assert len(data["participants"]) == 1
        assert data["participants"][0]["email"] == "john.doe@example.com"
    
    def test_create_meeting_without_participants(self, client):
        """Test creating a meeting without participants."""
        meeting_data = {
            "title": "Planning Session",
            "description": "Q4 Planning",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=2)).isoformat(),
        }
        
        response = client.post("/api/meetings/", json=meeting_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Planning Session"
        assert len(data["participants"]) == 0


class TestMeetingRetrieval:
    """Test meeting retrieval."""
    
    def test_get_all_meetings(self, client, sample_participant):
        """Test getting all meetings."""
        # Create a meeting first
        meeting_data = {
            "title": "Test Meeting",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).isoformat(),
            "participant_ids": [str(sample_participant.id)]
        }
        client.post("/api/meetings/", json=meeting_data)
        
        # Get all meetings
        response = client.get("/api/meetings/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestICSExport:
    """Test ICS export functionality."""
    
    def test_export_meeting_as_ics(self, client, sample_participant):
        """Test exporting a meeting as ICS file."""
        # Create a meeting
        meeting_data = {
            "title": "Board Meeting",
            "description": "Monthly board meeting",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=7, hours=2)).isoformat(),
            "location": "Boardroom",
            "participant_ids": [str(sample_participant.id)]
        }
        
        create_response = client.post("/api/meetings/", json=meeting_data)
        meeting_id = create_response.json()["id"]
        
        # Export as ICS
        response = client.get(f"/api/meetings/{meeting_id}/export")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/calendar; charset=utf-8"
        assert b"BEGIN:VCALENDAR" in response.content
        assert b"Board Meeting" in response.content
