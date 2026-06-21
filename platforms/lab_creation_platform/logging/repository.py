"""
Repository for 5W1H Logging data access layer.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import Session

from .models import LogEntry


class LogEntryRepository:
    """Repository for Log Entry operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, log_entry: LogEntry) -> LogEntry:
        """Create a new log entry."""
        self.session.add(log_entry)
        self.session.commit()
        self.session.refresh(log_entry)
        return log_entry

    def get(self, log_id: UUID) -> Optional[LogEntry]:
        """Get a log entry by ID."""
        return self.session.query(LogEntry).filter(LogEntry.id == log_id).first()

    def list_by_criteria(
        self,
        lab_instance_id: Optional[str] = None,
        lab_type_id: Optional[str] = None,
        user_id: Optional[str] = None,
        what: Optional[str] = None,
        validation_status: Optional[str] = None,
        impact_risk_level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        order_by_desc: bool = True
    ) -> List[LogEntry]:
        """List log entries by various criteria."""
        query = self.session.query(LogEntry)
        
        # Apply filters
        if lab_instance_id:
            query = query.filter(LogEntry.lab_instance_id == lab_instance_id)
        if lab_type_id:
            query = query.filter(LogEntry.lab_type_id == lab_type_id)
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
        if what:
            query = query.filter(LogEntry.what == what)
        if validation_status:
            query = query.filter(LogEntry.validation_status == validation_status)
        if impact_risk_level:
            query = query.filter(LogEntry.impact_risk_level == impact_risk_level)
        if start_time:
            query = query.filter(LogEntry.timestamp >= start_time)
        if end_time:
            query = query.filter(LogEntry.timestamp <= end_time)
        
        # Apply ordering
        if order_by_desc:
            query = query.order_by(LogEntry.timestamp.desc())
        else:
            query = query.order_by(LogEntry.timestamp.ascii)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()

    def get_recent_logs(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[LogEntry]:
        """Get recent log entries."""
        return self.session.query(LogEntry)\
            .order_by(LogEntry.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    def count_by_criteria(
        self,
        lab_instance_id: Optional[str] = None,
        lab_type_id: Optional[str] = None,
        user_id: Optional[str] = None,
        what: Optional[str] = None,
        validation_status: Optional[str] = None,
        impact_risk_level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count log entries by criteria."""
        query = self.session.query(LogEntry)
        
        # Apply filters (same as list_by_criteria)
        if lab_instance_id:
            query = query.filter(LogEntry.lab_instance_id == lab_instance_id)
        if lab_type_id:
            query = query.filter(LogEntry.lab_type_id == lab_type_id)
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
        if what:
            query = query.filter(LogEntry.what == what)
        if validation_status:
            query = query.filter(LogEntry.validation_status == validation_status)
        if impact_risk_level:
            query = query.filter(LogEntry.impact_risk_level == impact_risk_level)
        if start_time:
            query = query.filter(LogEntry.timestamp >= start_time)
        if end_time:
            query = query.filter(LogEntry.timestamp <= end_time)
        
        return query.count()

    def delete_old_logs(self, older_than: datetime) -> int:
        """Delete log entries older than a specified date."""
        to_delete = self.session.query(LogEntry)\
            .filter(LogEntry.timestamp < older_than)\
            .delete()
        self.session.commit()
        return to_delete
