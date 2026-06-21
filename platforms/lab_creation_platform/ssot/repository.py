"""
Repository for SSOT Entity data access layer.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from .models import SSOTEntity


class SSOTEntityRepository:
    """Repository for SSOT Entity operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, entity: SSOTEntity) -> SSOTEntity:
        """Create a new SSOT entity."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get(self, entity_id: UUID) -> Optional[SSOTEntity]:
        """Get an SSOT entity by ID."""
        result = self.session.execute(
            select(SSOTEntity).where(SSOTEntity.id == entity_id)
        )
        return result.scalar_one_or_none()

    def get_by_type_and_key(
        self, 
        entity_type: str, 
        entity_key: str,
        active_only: bool = True
    ) -> Optional[SSOTEntity]:
        """Get an SSOT entity by type and key."""
        query = select(SSOTEntity).where(
            SSOTEntity.entity_type == entity_type,
            SSOTEntity.entity_key == entity_key
        )
        if active_only:
            query = query.where(SSOTEntity.is_active == True)
        
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def list_by_type(
        self, 
        entity_type: str,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[SSOTEntity]:
        """List SSOT entities by type."""
        query = select(SSOTEntity).where(
            SSOTEntity.entity_type == entity_type
        )
        if active_only:
            query = query.where(SSOTEntity.is_active == True)
        
        query = query.offset(offset).limit(limit)
        
        result = self.session.execute(query)
        return list(result.scalars().all())

    def update(
        self, 
        entity_id: UUID, 
        **kwargs
    ) -> Optional[SSOTEntity]:
        """Update an SSOT entity."""
        # Remove None values to avoid overwriting with NULL
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        if not kwargs:
            return self.get(entity_id)
        
        kwargs['updated_at'] = datetime.utcnow()
        
        self.session.execute(
            update(SSOTEntity)
            .where(SSOTEntity.id == entity_id)
            .values(**kwargs)
        )
        self.session.commit()
        
        return self.get(entity_id)

    def increment_version(self, entity_id: UUID) -> Optional[SSOTEntity]:
        """Increment the version of an SSOT entity (for optimistic locking)."""
        self.session.execute(
            update(SSOTEntity)
            .where(SSOTEntity.id == entity_id)
            .values(
                version=SSOTEntity.version + 1,
                updated_at=datetime.utcnow()
            )
        )
        self.session.commit()
        return self.get(entity_id)

    def delete(self, entity_id: UUID) -> bool:
        """Soft delete an SSOT entity."""
        result = self.session.execute(
            update(SSOTEntity)
            .where(SSOTEntity.id == entity_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        self.session.commit()
        return result.rowcount > 0

    def hard_delete(self, entity_id: UUID) -> bool:
        """Hard delete an SSOT entity (use with caution)."""
        result = self.session.execute(
            delete(SSOTEntity).where(SSOTEntity.id == entity_id)
        )
        self.session.commit()
        return result.rowcount > 0
