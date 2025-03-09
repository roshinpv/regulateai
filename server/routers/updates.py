from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.RegulatoryUpdate])
async def get_updates(
    skip: int = 0, 
    limit: int = 100,
    regulation_id: Optional[str] = None,
    agency: Optional[str] = None,
    since: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.RegulatoryUpdate)
    
    if regulation_id:
        query = query.filter(models.RegulatoryUpdate.regulation_id == regulation_id)
    
    if agency:
        query = query.filter(models.RegulatoryUpdate.agency == agency)
    
    if since:
        query = query.filter(models.RegulatoryUpdate.date >= since)
    
    # Order by date (most recent first)
    query = query.order_by(models.RegulatoryUpdate.date.desc())
    
    updates = query.offset(skip).limit(limit).all()
    return updates

@router.get("/recent", response_model=List[schemas.RegulatoryUpdate])
async def get_recent_updates(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    since_date = datetime.utcnow() - timedelta(days=days)
    
    updates = db.query(models.RegulatoryUpdate).filter(
        models.RegulatoryUpdate.date >= since_date
    ).order_by(models.RegulatoryUpdate.date.desc()).all()
    
    return updates

@router.get("/{update_id}", response_model=schemas.RegulatoryUpdate)
async def get_update(
    update_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    update = db.query(models.RegulatoryUpdate).filter(models.RegulatoryUpdate.id == update_id).first()
    if update is None:
        raise HTTPException(status_code=404, detail="Update not found")
    return update

@router.post("/", response_model=schemas.RegulatoryUpdate)
async def create_update(
    update: schemas.RegulatoryUpdateCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    # Check if regulation exists
    regulation = db.query(models.Regulation).filter(models.Regulation.id == update.regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    db_update = models.RegulatoryUpdate(
        title=update.title,
        date=update.date,
        agency=update.agency,
        description=update.description,
        regulation_id=update.regulation_id
    )
    db.add(db_update)
    
    # Update the last_updated field of the regulation
    regulation.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(db_update)
    return db_update

@router.put("/{update_id}", response_model=schemas.RegulatoryUpdate)
async def update_regulatory_update(
    update_id: str,
    update: schemas.RegulatoryUpdateCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_update = db.query(models.RegulatoryUpdate).filter(models.RegulatoryUpdate.id == update_id).first()
    if db_update is None:
        raise HTTPException(status_code=404, detail="Update not found")
    
    # Check if regulation exists
    regulation = db.query(models.Regulation).filter(models.Regulation.id == update.regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    db_update.title = update.title
    db_update.date = update.date
    db_update.agency = update.agency
    db_update.description = update.description
    db_update.regulation_id = update.regulation_id
    
    db.commit()
    db.refresh(db_update)
    return db_update

@router.delete("/{update_id}")
async def delete_update(
    update_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_update = db.query(models.RegulatoryUpdate).filter(models.RegulatoryUpdate.id == update_id).first()
    if db_update is None:
        raise HTTPException(status_code=404, detail="Update not found")
    
    db.delete(db_update)
    db.commit()
    return {"message": "Update deleted successfully"}