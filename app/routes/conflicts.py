"""API routes for conflict detection."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ConflictCheckRequest, ConflictCheckResponse
from app.services.conflict_service import ConflictService

router = APIRouter(prefix="/api/conflicts", tags=["Conflicts"])


@router.post("/check", response_model=ConflictCheckResponse)
def check_conflicts(
    request: ConflictCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check for scheduling conflicts for given participants and time slot.
    
    Args:
        request: Conflict check request with participant IDs and time slot
        db: Database session
        
    Returns:
        Conflict check response with list of conflicts (if any)
    """
    has_conflicts, conflicts = ConflictService.check_conflicts(
        db=db,
        participant_ids=request.participant_ids,
        start_time=request.start_time,
        end_time=request.end_time,
        exclude_meeting_id=request.exclude_meeting_id
    )
    
    return ConflictCheckResponse(
        has_conflicts=has_conflicts,
        conflicts=conflicts
    )
