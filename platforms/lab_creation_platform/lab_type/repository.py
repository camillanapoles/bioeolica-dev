"""
Repository for Lab Type data access layer.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from .models import LabType


class LabTypeRepository:
    """Repository for Lab Type operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, lab_type: LabType) -> LabType:
        """Create a new lab type."""
        self.session.add(lab_type)
        self.session.commit()
        self.session.refresh(lab_type)
        return lab_type

    def get(self, lab_type_id: UUID) -> Optional[LabType]:
        """Get a lab type by ID."""
        return self.session.query(LabType).filter(LabType.id == lab_type_id).first()

    def get_by_name_and_version(
        self, 
        name: str,
        version_major: int,
        version_minor: int,
        version_patch: int
    ) -> Optional[LabType]:
        """Get a lab type by name and version."""
        return self.session.query(LabType).filter(
            LabType.name == name,
            LabType.version_major == version_major,
            LabType.version_minor == version_minor,
            LabType.version_patch == version_patch
        ).first()

    def get_latest_by_name(self, name: str) -> Optional[LabType]:
        """Get the latest published version of a lab type by name."""
        return self.session.query(LabType).filter(
            LabType.name == name,
            LabType.is_published == True
        ).order_by(
            LabType.version_major.desc(),
            LabType.version_minor.desc(),
            LabType.version_patch.desc()
        ).first()

    def list_by_name(
        self, 
        name: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[LabType]:
        """List all versions of a lab type by name."""
        return self.session.query(LabType).filter(
            LabType.name == name
        ).order_by(
            LabType.version_major.desc(),
            LabType.version_minor.desc(),
            LabType.version_patch.desc()
        ).offset(offset).limit(limit).all()

    def list_published(
        self, 
        domain_tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LabType]:
        """List published lab types, optionally filtered by domain tag."""
        query = self.session.query(LabType).filter(LabType.is_published == True)
        
        if domain_tag:
            # Filter by domain tag in the JSON array
            # This is a simplified approach; in production you'd use proper JSON querying
            query = query.filter(LabType.domain_tags.contains([domain_tag]))
        
        return query.order_by(
            LabType.version_major.desc(),
            LabType.version_minor.desc(),
            LabType.version_patch.desc()
        ).offset(offset).limit(limit).all()

    def update(
        self, 
        lab_type_id: UUID, 
        **kwargs
    ) -> Optional[LabType]:
        """Update a lab type."""
        # Remove None values to avoid overwriting with NULL
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        if not kwargs:
            return self.get(lab_type_id)
        
        kwargs['updated_at'] = datetime.utcnow()
        
        self.session.query(LabType).filter(LabType.id == lab_type_id).update(kwargs)
        self.session.commit()
        
        return self.get(lab_type_id)

    def publish(self, lab_type_id: UUID) -> Optional[LabType]:
        """Publish a lab type (make it available for instantiation)."""
        lab_type = self.get(lab_type_id)
        if not lab_type:
            return None
            
        lab_type.is_published = True
        lab_type.updated_at = datetime.utcnow()
        
        self.session.commit()
        self.session.refresh(lab_type)
        return lab_type

    def unpublish(self, lab_type_id: UUID) -> Optional[LabType]:
        """Unpublish a lab type."""
        lab_type = self.get(lab_type_id)
        if not lab_type:
            return None
            
        lab_type.is_published = False
        lab_type.updated_at = datetime.utcnow()
        
        self.session.commit()
        self.session.refresh(lab_type)
        return lab_type

    def delete(self, lab_type_id: UUID) -> bool:
        """Delete a lab type."""
        lab_type = self.get(lab_type_id)
        if not lab_type:
            return False
            
        self.session.delete(lab_type)
        self.session.commit()
        return True
