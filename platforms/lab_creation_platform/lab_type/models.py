"""
SQLAlchemy models for the Lab Type Definition service.
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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LabType(Base):
    """Definition of a lab type that specifies stages, data model, workflow, etc."""
    __tablename__ = "lab_types"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)  # e.g., 'Microchip Recycling for Tobogã'
    description = Column(Text)  # Detailed description of the lab type
    version_major = Column(Integer, nullable=False, default=0)  # Semantic versioning
    version_minor = Column(Integer, nullable=False, default=0)
    version_patch = Column(Integer, nullable=False, default=0)
    
    # Lab type definition stored as JSON
    definition = Column(JSON, nullable=False)  # Contains stages, data model, workflow, visualization, etc.
    
    # Metadata
    domain_tags = Column(JSON)  # e.g., ["materials", "recycling", "e-waste"]
    scope_description = Column(Text)  # Describes the boundaries/scope of this lab type
    is_published = Column(Boolean, nullable=False, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255))  # User ID or username who created this
    
    # Ensure unique name/version combination
    __table_args__ = (
        UniqueConstraint('name', 'version_major', 'version_minor', 'version_patch',
                        name='uq_lab_type_name_version'),
        Index('ix_lab_type_name', 'name'),
        Index('ix_lab_type_published', 'is_published'),
    )

    def __repr__(self) -> str:
        return f"<LabType {self.name} v{self.version_major}.{self.version_minor}.{self.version_patch}>"
        
    @property
    def version_string(self) -> str:
        return f"{self.version_major}.{self.version_minor}.{self.version_patch}"
