"""Tests for conflict detection."""

from datetime import datetime, timezone, timedelta
import pytest


class TestConflictDetection:
    """Test conflict detection functionality."""
    
    def test_no_conflicts(self, client, sample_participant, sample_participant2):
        """Test when there are no scheduling conflicts."""
        # Create a meeting
        meeting_data = {
            "title": "Morning Meeting",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=9)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=10)).isoformat(),
            "participant_ids": [str(sample_participant.id)]
        }
        client.post("/api/meetings/", json=meeting_data)
        
        # Check for conflicts in a different time slot
        conflict_check = {
            "participant_ids": [str(sample_participant.id)],
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=14)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=15)).isoformat()
        }
        
        response = client.post("/api/conflicts/check", json=conflict_check)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_conflicts"] is False
        assert len(data["conflicts"]) == 0
    
    def test_overlapping_conflicts(self, client, sample_participant):
        """Test detection of overlapping meetings."""
        # Create first meeting (9 AM - 10 AM)
        meeting1 = {
            "title": "Meeting 1",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=9)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=10)).isoformat(),
            "participant_ids": [str(sample_participant.id)]
        }
        client.post("/api/meetings/", json=meeting1)
        
        # Check for conflicts with overlapping time (9:30 AM - 10:30 AM)
        conflict_check = {
            "participant_ids": [str(sample_participant.id)],
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=9.5)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=10.5)).isoformat()
        }
        
        response = client.post("/api/conflicts/check", json=conflict_check)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_conflicts"] is True
        assert len(data["conflicts"]) > 0
        assert data["conflicts"][0]["participant_id"] == str(sample_participant.id)
    
    def test_multiple_participant_conflicts(self, client, sample_participant, sample_participant2):
        """Test conflict detection with multiple participants."""
        # Create meetings for both participants at different times
        meeting1 = {
            "title": "Meeting A",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=10)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=11)).isoformat(),
            "participant_ids": [str(sample_participant.id)]
        }
        client.post("/api/meetings/", json=meeting1)
        
        meeting2 = {
            "title": "Meeting B",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=14)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=15)).isoformat(),
            "participant_ids": [str(sample_participant2.id)]
        }
        client.post("/api/meetings/", json=meeting2)
        
        # Check for conflicts at 10:30 AM (conflicts with participant 1 only)
        conflict_check = {
            "participant_ids": [str(sample_participant.id), str(sample_participant2.id)],
            "start_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=10.5)).isoformat(),
            "end_time": (datetime.now(timezone.utc) + timedelta(days=2, hours=11.5)).isoformat()
        }
        
        response = client.post("/api/conflicts/check", json=conflict_check)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_conflicts"] is True
        # Should only have conflict for sample_participant, not sample_participant2
        assert len(data["conflicts"]) == 1
        assert data["conflicts"][0]["participant_id"] == str(sample_participant.id)
