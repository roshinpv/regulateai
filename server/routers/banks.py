from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Bank])
async def get_banks(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    banks = db.query(models.Bank).offset(skip).limit(limit).all()
    return banks

@router.get("/{bank_id}", response_model=schemas.Bank)
async def get_bank(
    bank_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
    if bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank

@router.post("/", response_model=schemas.Bank)
async def create_bank(
    bank: schemas.BankCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_bank = models.Bank(
        name=bank.name
    )
    db.add(db_bank)
    db.commit()
    db.refresh(db_bank)
    return db_bank

@router.put("/{bank_id}", response_model=schemas.Bank)
async def update_bank(
    bank_id: str,
    bank: schemas.BankCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
    if db_bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    db_bank.name = bank.name
    
    db.commit()
    db.refresh(db_bank)
    return db_bank

@router.delete("/{bank_id}")
async def delete_bank(
    bank_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
    if db_bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    db.delete(db_bank)
    db.commit()
    return {"message": "Bank deleted successfully"}

@router.get("/{bank_id}/regulations", response_model=List[schemas.Regulation])
async def get_bank_regulations(
    bank_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
    if bank is None:
        raise HTTPException(status_code=404, detail="Bank not found")
    
    return bank.affected_regulations