"""
SQLAlchemy models for the 5W1H Logging service.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    Boolean,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LogEntry(Base):
    """Structured 5W1H log entry for tracking all platform actions."""
    __tablename__ = "log_entries"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String(255), index=True)  # For correlating logs across services
    span_id = Column(String(255), index=True)   # For distributed tracing
    
    # 5W1H Components
    what = Column(String(255), nullable=False, index=True)  # Action verb + object (e.g., "Created Lab Type")
    why = Column(Text)  # Justification from user or system
    who_type = Column(String(50))  # user|system|agent
    who_id = Column(String(255))   # UUID or agent_name
    who_role = Column(String(50))  # designer|user|admin|agent
    
    # When
    when_start = Column(DateTime, nullable=False)
    when_end = Column(DateTime, nullable=False)
    when_duration_ms = Column(Integer)  # Calculated duration
    
    # Where
    where_lab_stage = Column(String(100))  # e.g., 'planning', 'desenvolvimento'
    where_component = Column(String(255))  # e.g., 'frontend.forms.lab_type_input', 'backend.ssot.service'
    where_file_path = Column(String(500))  # If applicable
    where_line_number = Column(Integer)    # If applicable
    where_git_commit = Column(String(40))  # If code change
    
    # How
    how_method = Column(String(100))  # e.g., 'FORM_SUBMIT', 'API_CALL', 'SOLVER_EXECUTION'
    how_tools = Column(JSON)          # List of tools used (e.g., ["OpenFOAM v10", "FEniCS 2025.1"])
    how_parameters = Column(JSON)     # Inputs to the action
    how_environment = Column(String(50))  # e.g., 'staging', 'production', 'dev'
    
    # Inputs and Outputs (references to other entities)
    inputs = Column(JSON)  # List of resource IDs or references
    outputs = Column(JSON) # List of resource IDs or references
    
    # Validation
    validation_status = Column(String(50))  # PASS|FAIL|PENDING|SKIPPED
    validation_method = Column(String(100)) # e.g., 'UNIT_TEST', 'GITNEXUS_IMPACT'
    validation_reference = Column(Text)     # e.g., 'DOI:10.1016/j.matpr.2024.01.123'
    validation_details = Column(Text)       # Optional elaboration
    
    # Next steps (suggested actions)
    next_steps = Column(JSON)  # List of suggested actions
    
    # Impact analysis (auto-populated for M0/M8)
    impact_risk_level = Column(String(20))  # LOW|MEDIUM|HIGH|CRITICAL
    impact_affected_symbols = Column(Integer)  # Count of affected symbols
    impact_affected_processes = Column(Integer) # Count of affected processes
    impact_blast_radius_description = Column(Text)
    
    # PQMS impact (how this action affects PQMS dimensions)
    pqms_dimension_scores = Column(JSON)  # Dictionary of dimension scores
    pqms_delta_explanation = Column(Text)
    
    # Contextual information
    lab_instance_id = Column(String(255), index=True)  # UUID of lab instance
    lab_type_id = Column(String(255), index=True)      # UUID of lab type
    lab_type_version = Column(String(50))              # Semver string
    user_id = Column(String(255), index=True)          # UUID of user
    session_id = Column(String(255))                   # Session identifier
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('ix_log_timestamp', 'timestamp'),
        Index('ix_log_lab_instance', 'lab_instance_id'),
        Index('ix_log_lab_type', 'lab_type_id'),
        Index('ix_log_user', 'user_id'),
        Index('ix_log_what', 'what'),
        Index('ix_log_validation_status', 'validation_status'),
        Index('ix_log_impact_risk', 'impact_risk_level'),
    )

    def __repr__(self) -> str:
        return f"<LogEntry {self.what} at {self.timestamp}>"
