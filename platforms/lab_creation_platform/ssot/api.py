from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .models import SSOTEntity
from .repository import SSOTEntityRepository
from shared.database import get_db

from pydantic import BaseModel

router = APIRouter(prefix="/ssot", tags=["ssot"])
"""
API routes for the Single Source of Truth (SSOT) service.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .models import SSOTEntity
from .repository import SSOTEntityRepository
from shared.database import get_db

router = APIRouter(prefix="/ssot", tags=["ssot"])


# Pydantic models for request/response
class SSOTEntityBase(BaseModel):
    entity_type: str
    entity_key: str
    value: Dict[str, Any]
    source: Optional[str] = None


class SSOTEntityCreate(SSOTEntityBase):
    pass


class SSOTEntityUpdate(BaseModel):
    value: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    is_active: Optional[bool] = None


class SSOTEntityResponse(SSOTEntityBase):
    id: UUID
    version: int
    retrieved_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


@router.post("/entities/", response_model=SSOTEntityResponse, status_code=status.HTTP_201_CREATED)
def create_ssot_entity(
    entity: SSOTEntityCreate,
    db: Session = Depends(get_db)
):
    """Create a new SSOT entity."""
    # Check if entity already exists
    db_entity = SSOTEntityRepository(db).get_by_type_and_key(
        entity.entity_type, 
        entity.entity_key,
        active_only=False  # Check both active and inactive
    )
    if db_entity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SSOT entity {entity.entity_type}:{entity.entity_key} already exists"
        )
    
    # Create new entity
    db_entity = SSOTEntity(
        **entity.dict(),
        retrieved_at=datetime.utcnow()
    )
    return SSOTEntityRepository(db).create(db_entity)


@router.get("/entities/{entity_id}", response_model=SSOTEntityResponse)
def get_ssot_entity(
    entity_id: UUID,
    db: Session = Depends(get_db)
):
    """Get an SSOT entity by ID."""
    db_entity = SSOTEntityRepository(db).get(entity_id)
    if not db_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSOT entity not found"
        )
    return db_entity


@router.get("/entities/", response_model=List[SSOTEntityResponse])
def list_ssot_entities(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    active_only: bool = Query(True, description="Return only active entities"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List SSOT entities with optional filtering."""
    if entity_type:
        entities = SSOTEntityRepository(db).list_by_type(
            entity_type=entity_type,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
    else:
        # For simplicity, if no type specified, we'll return an empty list
        # In a full implementation, we'd query all types
        entities = []
    
    return entities


@router.get("/entities/by-type-key/", response_model=SSOTEntityResponse)
def get_ssot_entity_by_type_key(
    entity_type: str = Query(..., description="Entity type"),
    entity_key: str = Query(..., description="Entity key"),
    active_only: bool = Query(True, description="Return only if active"),
    db: Session = Depends(get_db)
):
    """Get an SSOT entity by type and key."""
    db_entity = SSOTEntityRepository(db).get_by_type_and_key(
        entity_type=entity_type,
        entity_key=entity_key,
        active_only=active_only
    )
    if not db_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SSOT entity {entity_type}:{entity_key} not found"
        )
    return db_entity


@router.put("/entities/{entity_id}", response_model=SSOTEntityResponse)
def update_ssot_entity(
    entity_id: UUID,
    entity_update: SSOTEntityUpdate,
    db: Session = Depends(get_db)
):
    """Update an SSOT entity."""
    db_entity = SSOTEntityRepository(db).get(entity_id)
    if not db_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSOT entity not found"
        )
    
    # Update the entity
    update_data = entity_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )
    
    updated_entity = SSOTEntityRepository(db).update(
        entity_id=entity_id,
        **update_data
    )
    
    # Increment version for optimistic locking
    SSOTEntityRepository(db).increment_version(entity_id)
    
    return SSOTEntityRepository(db).get(entity_id)


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ssot_entity(
    entity_id: UUID,
    db: Session = Depends(get_db)
):
    """Soft delete an SSOT entity."""
    db_entity = SSOTEntityRepository(db).get(entity_id)
    if not db_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSOT entity not found"
        )
    
    success = SSOTEntityRepository(db).delete(entity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete SSOT entity"
        )
    
    return None
