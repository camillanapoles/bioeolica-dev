"""
SQLAlchemy models for the Single Source of Truth (SSOT) service.
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


class SSOTEntity(Base):
    """Single Source of Truth entity for storing lab-relevant constants and reference data."""
    __tablename__ = "ssot_entities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(100), nullable=False, index=True)  # e.g., 'material', 'process_constant', 'solver_parameter'
    entity_key = Column(String(255), nullable=False, index=True)  # e.g., 'youngs_modulus_si', 'mars_gravity'
    value = Column(JSON, nullable=False)  # Stores the actual value as JSON
    version = Column(Integer, nullable=False, default=1)  # For optimistic locking
    source = Column(Text)  # Source of the data (e.g., 'NIST Database v3.2', 'Experimental Measurement')
    retrieved_at = Column(DateTime)  # When this data was retrieved from source
    is_active = Column(Boolean, nullable=False, default=True)  # Soft delete flag
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Composite index for frequent lookups
    __table_args__ = (
        Index('ix_ssot_entity_type_key', 'entity_type', 'entity_key'),
        Index('ix_ssot_active_type_key', 'is_active', 'entity_type', 'entity_key'),
    )

    def __repr__(self) -> str:
        return f"<SSOTEntity {self.entity_type}:{self.entity_key} v{self.version}>"
