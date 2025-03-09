from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Agency])
async def get_agencies(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    agencies = db.query(models.Agency).offset(skip).limit(limit).all()
    return agencies

@router.get("/{agency_id}", response_model=schemas.Agency)
async def get_agency(
    agency_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    agency = db.query(models.Agency).filter(models.Agency.id == agency_id).first()
    if agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    return agency

@router.post("/", response_model=schemas.Agency)
async def create_agency(
    agency: schemas.AgencyCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_agency = models.Agency(
        name=agency.name,
        description=agency.description
    )
    db.add(db_agency)
    db.commit()
    db.refresh(db_agency)
    return db_agency

@router.put("/{agency_id}", response_model=schemas.Agency)
async def update_agency(
    agency_id: str,
    agency: schemas.AgencyCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_agency = db.query(models.Agency).filter(models.Agency.id == agency_id).first()
    if db_agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    db_agency.name = agency.name
    db_agency.description = agency.description
    
    db.commit()
    db.refresh(db_agency)
    return db_agency

@router.delete("/{agency_id}")
async def delete_agency(
    agency_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_agency = db.query(models.Agency).filter(models.Agency.id == agency_id).first()
    if db_agency is None:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    # Check if agency has regulations
    regulations = db.query(models.Regulation).filter(models.Regulation.agency_id == agency_id).all()
    if regulations:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete agency with associated regulations. Remove regulations first."
        )
    
    db.delete(db_agency)
    db.commit()
    return {"message": "Agency deleted successfully"}