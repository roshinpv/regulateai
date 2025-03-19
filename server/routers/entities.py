import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List, Optional
from datetime import datetime
import logging

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user
from ..llm.rag import rag_engine

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.Entity])
async def get_entities(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    min_risk_score: Optional[int] = None,
    max_risk_score: Optional[int] = None,
    analysis_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all entities with optional filtering."""
    query = db.query(models.Entity)
    
    if entity_type:
        query = query.filter(models.Entity.type == entity_type)
    
    if min_risk_score is not None:
        query = query.filter(models.Entity.risk_score >= min_risk_score)
    
    if max_risk_score is not None:
        query = query.filter(models.Entity.risk_score <= max_risk_score)
    
    if analysis_status:
        query = query.filter(models.Entity.analysis_status == analysis_status)
    
    return query.offset(skip).limit(limit).all()

@router.get("/search", response_model=List[schemas.EntitySearchResult])
async def search_entities(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Search entities using RAG."""
    try:
        # Use RAG to find relevant entities
        search_results = await rag_engine.search_entities(query, limit)
        return search_results
    except Exception as e:
        logger.error(f"Error searching entities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error performing entity search"
        )

@router.get("/{entity_id}", response_model=schemas.Entity)
async def get_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get entity by ID."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.post("/", response_model=schemas.Entity)
async def create_entity(
    entity: schemas.EntityCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Create a new entity."""
    db_entity = models.Entity(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.put("/{entity_id}", response_model=schemas.Entity)
async def update_entity(
    entity_id: str,
    entity: schemas.EntityUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Update an entity."""
    db_entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    for key, value in entity.dict(exclude_unset=True).items():
        setattr(db_entity, key, value)
    
    db_entity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    """Delete an entity."""
    db_entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    db.delete(db_entity)
    db.commit()
    return {"message": "Entity deleted successfully"}

@router.post("/{entity_id}/analyze", response_model=schemas.Entity)
async def analyze_entity(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Analyze an entity and update its risk score."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    try:
        # Trigger risk score update
        db.execute(
            text("SELECT update_entity_risk_score(:entity_id)"),
            {"entity_id": entity_id}
        )
        db.commit()
        db.refresh(entity)
        return entity
    except Exception as e:
        logger.error(f"Error analyzing entity: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error analyzing entity"
        )

@router.get("/{entity_id}/sources", response_model=List[schemas.EntitySource])
async def get_entity_sources(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all sources for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return db.query(models.EntitySource).filter(
        models.EntitySource.entity_id == entity_id
    ).all()

@router.get("/{entity_id}/transactions", response_model=List[schemas.EntityTransaction])
async def get_entity_transactions(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all transactions for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return db.query(models.EntityTransaction).filter(
        models.EntityTransaction.entity_id == entity_id
    ).all()

@router.get("/{entity_id}/relationships", response_model=List[schemas.EntityRelationship])
async def get_entity_relationships(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all relationships for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return db.query(models.EntityRelationship).filter(
        (models.EntityRelationship.from_entity_id == entity_id) |
        (models.EntityRelationship.to_entity_id == entity_id)
    ).all()

@router.get("/{entity_id}/risk-factors", response_model=List[schemas.EntityRiskFactor])
async def get_entity_risk_factors(
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get all risk factors for an entity."""
    entity = db.query(models.Entity).filter(models.Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return db.query(models.EntityRiskFactor).filter(
        models.EntityRiskFactor.entity_id == entity_id
    ).all()