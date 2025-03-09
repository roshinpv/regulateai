from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Jurisdiction])
async def get_jurisdictions(
    skip: int = 0, 
    limit: int = 100,
    type: Optional[str] = None,
    parent_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.Jurisdiction)
    
    if type:
        query = query.filter(models.Jurisdiction.type == type)
    
    if parent_id:
        query = query.filter(models.Jurisdiction.parent_id == parent_id)
    else:
        # If no parent_id is specified, return top-level jurisdictions
        query = query.filter(models.Jurisdiction.parent_id == None)
    
    jurisdictions = query.offset(skip).limit(limit).all()
    return jurisdictions

@router.get("/{jurisdiction_id}", response_model=schemas.Jurisdiction)
async def get_jurisdiction(
    jurisdiction_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    return jurisdiction

@router.post("/", response_model=schemas.Jurisdiction)
async def create_jurisdiction(
    jurisdiction: schemas.JurisdictionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    # Check if parent jurisdiction exists if provided
    if jurisdiction.parent_id:
        parent = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent jurisdiction not found")
    
    db_jurisdiction = models.Jurisdiction(
        name=jurisdiction.name,
        code=jurisdiction.code,
        type=jurisdiction.type,
        parent_id=jurisdiction.parent_id
    )
    db.add(db_jurisdiction)
    db.commit()
    db.refresh(db_jurisdiction)
    return db_jurisdiction

@router.put("/{jurisdiction_id}", response_model=schemas.Jurisdiction)
async def update_jurisdiction(
    jurisdiction_id: str,
    jurisdiction: schemas.JurisdictionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if db_jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    # Check if parent jurisdiction exists if provided
    if jurisdiction.parent_id:
        parent = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent jurisdiction not found")
        
        # Prevent circular references
        if jurisdiction.parent_id == jurisdiction_id:
            raise HTTPException(status_code=400, detail="A jurisdiction cannot be its own parent")
    
    db_jurisdiction.name = jurisdiction.name
    db_jurisdiction.code = jurisdiction.code
    db_jurisdiction.type = jurisdiction.type
    db_jurisdiction.parent_id = jurisdiction.parent_id
    
    db.commit()
    db.refresh(db_jurisdiction)
    return db_jurisdiction

@router.delete("/{jurisdiction_id}")
async def delete_jurisdiction(
    jurisdiction_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if db_jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    # Check if jurisdiction has sub-jurisdictions
    sub_jurisdictions = db.query(models.Jurisdiction).filter(models.Jurisdiction.parent_id == jurisdiction_id).all()
    if sub_jurisdictions:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete jurisdiction with sub-jurisdictions. Remove sub-jurisdictions first."
        )
    
    # Check if jurisdiction has regulations
    regulations = db.query(models.Regulation).filter(models.Regulation.jurisdiction_id == jurisdiction_id).all()
    if regulations:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete jurisdiction with associated regulations. Remove regulations first."
        )
    
    db.delete(db_jurisdiction)
    db.commit()
    return {"message": "Jurisdiction deleted successfully"}

@router.get("/{jurisdiction_id}/regulations", response_model=List[schemas.Regulation])
async def get_jurisdiction_regulations(
    jurisdiction_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    regulations = db.query(models.Regulation).filter(
        models.Regulation.jurisdiction_id == jurisdiction_id
    ).offset(skip).limit(limit).all()
    
    return regulations

@router.get("/{jurisdiction_id}/agencies", response_model=List[schemas.Agency])
async def get_jurisdiction_agencies(
    jurisdiction_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    agencies = db.query(models.Agency).filter(
        models.Agency.jurisdiction_id == jurisdiction_id
    ).offset(skip).limit(limit).all()
    
    return agencies

@router.get("/{jurisdiction_id}/banks", response_model=List[schemas.Bank])
async def get_jurisdiction_banks(
    jurisdiction_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
    if jurisdiction is None:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
    
    banks = db.query(models.Bank).filter(
        models.Bank.jurisdiction_id == jurisdiction_id
    ).offset(skip).limit(limit).all()
    
    return banks