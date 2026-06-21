from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .models import LogEntry
from .repository import LogEntryRepository
from shared.database import get_db

from pydantic import BaseModel

router = APIRouter(prefix="/logs", tags=["logs"])
"""
API routes for the 5W1H Logging service.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .models import LogEntry
from .repository import LogEntryRepository
from shared.database import get_db

router = APIRouter(prefix="/logs", tags=["logs"])


# Pydantic models for request/response
class LogEntryBase(BaseModel):
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # 5W1H Components
    what: str
    why: Optional[str] = None
    who_type: Optional[str] = None
    who_id: Optional[str] = None
    who_role: Optional[str] = None
    
    # When
    when_start: datetime
    when_end: datetime
    when_duration_ms: Optional[int] = None
    
    # Where
    where_lab_stage: Optional[str] = None
    where_component: Optional[str] = None
    where_file_path: Optional[str] = None
    where_line_number: Optional[int] = None
    where_git_commit: Optional[str] = None
    
    # How
    how_method: Optional[str] = None
    how_tools: Optional[List[str]] = None
    how_parameters: Optional[Dict[str, Any]] = None
    how_environment: Optional[str] = None
    
    # Inputs and Outputs
    inputs: Optional[List[Any]] = None
    outputs: Optional[List[Any]] = None
    
    # Validation
    validation_status: Optional[str] = None
    validation_method: Optional[str] = None
    validation_reference: Optional[str] = None
    validation_details: Optional[str] = None
    
    # Next steps
    next_steps: Optional[List[str]] = None
    
    # Impact analysis
    impact_risk_level: Optional[str] = None
    impact_affected_symbols: Optional[int] = None
    impact_affected_processes: Optional[int] = None
    impact_blast_radius_description: Optional[str] = None
    
    # PQMS impact
    pqms_dimension_scores: Optional[Dict[str, float]] = None
    pqms_delta_explanation: Optional[str] = None
    
    # Contextual information
    lab_instance_id: Optional[str] = None
    lab_type_id: Optional[str] = None
    lab_type_version: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class LogEntryCreate(LogEntryBase):
    pass


class LogEntryResponse(LogEntryBase):
    id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True


class LogQueryParams(BaseModel):
    lab_instance_id: Optional[str] = None
    lab_type_id: Optional[str] = None
    user_id: Optional[str] = None
    what: Optional[str] = None
    validation_status: Optional[str] = None
    impact_risk_level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Query(100, ge=1, le=1000)
    offset: int = Query(0, ge=0)


@router.post("/", response_model=LogEntryResponse, status_code=status.HTTP_201_CREATED)
def create_log_entry(
    log_entry: LogEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new log entry."""
    db_log_entry = LogEntry(**log_entry.dict())
    return LogEntryRepository(db).create(db_log_entry)


@router.get("/{log_id}", response_model=LogEntryResponse)
def get_log_entry(
    log_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a log entry by ID."""
    db_log_entry = LogEntryRepository(db).get(log_id)
    if not db_log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found"
        )
    return db_log_entry


@router.get("/", response_model=List[LogEntryResponse])
def list_log_entries(
    lab_instance_id: Optional[str] = Query(None, description="Filter by lab instance ID"),
    lab_type_id: Optional[str] = Query(None, description="Filter by lab type ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    what: Optional[str] = Query(None, description="Filter by action (what)"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    impact_risk_level: Optional[str] = Query(None, description="Filter by impact risk level"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time (inclusive)"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time (inclusive)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List log entries with filtering options."""
    logs = LogEntryRepository(db).list_by_criteria(
        lab_instance_id=lab_instance_id,
        lab_type_id=lab_type_id,
        user_id=user_id,
        what=what,
        validation_status=validation_status,
        impact_risk_level=impact_risk_level,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    return logs


@router.get("/recent/", response_model=List[LogEntryResponse])
def get_recent_logs(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get recent log entries."""
    logs = LogEntryRepository(db).get_recent_logs(limit=limit, offset=offset)
    return logs


@router.get("/count/")
def count_log_entries(
    lab_instance_id: Optional[str] = Query(None, description="Filter by lab instance ID"),
    lab_type_id: Optional[str] = Query(None, description="Filter by lab type ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    what: Optional[str] = Query(None, description="Filter by action (what)"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    impact_risk_level: Optional[str] = Query(None, description="Filter by impact risk level"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time (inclusive)"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time (inclusive)"),
    db: Session = Depends(get_db)
):
    """Count log entries with filtering options."""
    count = LogEntryRepository(db).count_by_criteria(
        lab_instance_id=lab_instance_id,
        lab_type_id=lab_type_id,
        user_id=user_id,
        what=what,
        validation_status=validation_status,
        impact_risk_level=impact_risk_level,
        start_time=start_time,
        end_time=end_time
    )
    return {"count": count}


@router.delete("/cleanup/")
def cleanup_old_logs(
    older_than_days: int = Query(30, ge=1, description="Delete logs older than this many days"),
    db: Session = Depends(get_db)
):
    """Clean up old log entries."""
    cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
    deleted_count = LogEntryRepository(db).delete_old_logs(cutoff_date)
    return {
        "message": f"Deleted {deleted_count} log entries older than {older_than_days} days",
        "deleted_count": deleted_count
    }
