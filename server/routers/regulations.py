from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.Regulation])
async def get_regulations(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    impact_level: Optional[str] = None,
    agency_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.Regulation)
    
    if category:
        # Filter by category using the association table
        query = query.join(models.RegulationCategoryAssociation).filter(
            models.RegulationCategoryAssociation.category == category
        )
    
    if impact_level:
        query = query.filter(models.Regulation.impact_level == impact_level)
    
    if agency_id:
        query = query.filter(models.Regulation.agency_id == agency_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.Regulation.title.ilike(search_term)) | 
            (models.Regulation.summary.ilike(search_term))
        )
    
    # Eager load all relationships
    query = query.options(
        joinedload(models.Regulation.agency),
        joinedload(models.Regulation.jurisdiction),
        joinedload(models.Regulation.compliance_steps),
        joinedload(models.Regulation.affected_banks),
        joinedload(models.Regulation.updates),
        joinedload(models.Regulation.alerts),
        joinedload(models.Regulation.responsible_units),
        joinedload(models.Regulation.categories),
        joinedload(models.Regulation.related_regulations)
    )
    
    regulations = query.offset(skip).limit(limit).all()
    return regulations

@router.get("/{regulation_id}", response_model=schemas.Regulation)
async def get_regulation(
    regulation_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Query with eager loading of all relationships
    regulation = db.query(models.Regulation).options(
        joinedload(models.Regulation.agency),
        joinedload(models.Regulation.jurisdiction),
        joinedload(models.Regulation.compliance_steps),
        joinedload(models.Regulation.affected_banks),
        joinedload(models.Regulation.updates),
        joinedload(models.Regulation.alerts),
        joinedload(models.Regulation.responsible_units),
        joinedload(models.Regulation.categories),
        joinedload(models.Regulation.related_regulations)
    ).filter(models.Regulation.id == regulation_id).first()
    
    if regulation is None:
        raise HTTPException(status_code=404, detail="Regulation not found")
    return regulation

@router.post("/", response_model=schemas.Regulation)
async def create_regulation(
    regulation: schemas.RegulationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    # Check if agency exists
    agency = db.query(models.Agency).filter(models.Agency.id == regulation.agency_id).first()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    
    # Create regulation
    db_regulation = models.Regulation(
        title=regulation.title,
        agency_id=regulation.agency_id,
        impact_level=regulation.impact_level,
        summary=regulation.summary,
        jurisdiction_id=regulation.jurisdiction_id,
        effective_date=regulation.effective_date,
        compliance_deadline=regulation.compliance_deadline,
        source_url=regulation.source_url,
        official_reference=regulation.official_reference,
        last_updated=datetime.utcnow()
    )
    
    # Add categories
    for category in regulation.categories:
        cat_assoc = models.RegulationCategoryAssociation(
            regulation_id=db_regulation.id,
            category=category
        )
        db_regulation.categories.append(cat_assoc)
    
    db.add(db_regulation)
    db.commit()
    
    # Add compliance steps
    for step in regulation.compliance_steps:
        db_step = models.ComplianceStep(
            regulation_id=db_regulation.id,
            description=step.description,
            order=step.order
        )
        db.add(db_step)
    
    # Add affected banks
    if regulation.affected_bank_ids:
        for bank_id in regulation.affected_bank_ids:
            bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
            if bank:
                db_regulation.affected_banks.append(bank)
    
    db.commit()
    db.refresh(db_regulation)
    return db_regulation

@router.put("/{regulation_id}", response_model=schemas.Regulation)
async def update_regulation(
    regulation_id: str,
    regulation: schemas.RegulationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_regulation = db.query(models.Regulation).filter(models.Regulation.id == regulation_id).first()
    if db_regulation is None:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    # Update regulation fields
    db_regulation.title = regulation.title
    db_regulation.agency_id = regulation.agency_id
    db_regulation.impact_level = regulation.impact_level
    db_regulation.summary = regulation.summary
    db_regulation.jurisdiction_id = regulation.jurisdiction_id
    db_regulation.effective_date = regulation.effective_date
    db_regulation.compliance_deadline = regulation.compliance_deadline
    db_regulation.source_url = regulation.source_url
    db_regulation.official_reference = regulation.official_reference
    db_regulation.last_updated = datetime.utcnow()
    
    # Update categories
    db_regulation.categories = []
    for category in regulation.categories:
        cat_assoc = models.RegulationCategoryAssociation(
            regulation_id=db_regulation.id,
            category=category
        )
        db_regulation.categories.append(cat_assoc)
    
    # Update compliance steps
    # First, remove existing steps
    db.query(models.ComplianceStep).filter(models.ComplianceStep.regulation_id == regulation_id).delete()
    
    # Add new steps
    for step in regulation.compliance_steps:
        db_step = models.ComplianceStep(
            regulation_id=db_regulation.id,
            description=step.description,
            order=step.order
        )
        db.add(db_step)
    
    # Update affected banks
    db_regulation.affected_banks = []
    if regulation.affected_bank_ids:
        for bank_id in regulation.affected_bank_ids:
            bank = db.query(models.Bank).filter(models.Bank.id == bank_id).first()
            if bank:
                db_regulation.affected_banks.append(bank)
    
    db.commit()
    db.refresh(db_regulation)
    return db_regulation

@router.delete("/{regulation_id}")
async def delete_regulation(
    regulation_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_regulation = db.query(models.Regulation).filter(models.Regulation.id == regulation_id).first()
    if db_regulation is None:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    db.delete(db_regulation)
    db.commit()
    return {"message": "Regulation deleted successfully"}

@router.get("/search/natural", response_model=List[schemas.Regulation])
async def natural_language_search(
    query: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # This is a simplified implementation of natural language search
    # In a real application, you would use a more sophisticated approach
    # such as embedding-based search or a dedicated search engine
    
    search_terms = query.lower().split()
    results = []
    
    # Query with eager loading
    regulations = db.query(models.Regulation).options(
        joinedload(models.Regulation.agency),
        joinedload(models.Regulation.jurisdiction),
        joinedload(models.Regulation.compliance_steps),
        joinedload(models.Regulation.affected_banks),
        joinedload(models.Regulation.updates),
        joinedload(models.Regulation.alerts),
        joinedload(models.Regulation.responsible_units),
        joinedload(models.Regulation.categories),
        joinedload(models.Regulation.related_regulations)
    ).all()
    
    for regulation in regulations:
        score = 0
        title_lower = regulation.title.lower()
        summary_lower = regulation.summary.lower()
        
        for term in search_terms:
            if term in title_lower:
                score += 3  # Higher weight for title matches
            if term in summary_lower:
                score += 1
        
        if score > 0:
            results.append((regulation, score))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in results[:10]]