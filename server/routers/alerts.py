from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

@router.get("/", response_model=List[schemas.ComplianceAlert])
async def get_alerts(
    skip: int = 0, 
    limit: int = 100,
    priority: Optional[str] = None,
    regulation_id: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.ComplianceAlert)
    
    if priority:
        query = query.filter(models.ComplianceAlert.priority == priority)
    
    if regulation_id:
        query = query.filter(models.ComplianceAlert.regulation_id == regulation_id)
    
    if due_before:
        query = query.filter(models.ComplianceAlert.due_date <= due_before)
    
    if due_after:
        query = query.filter(models.ComplianceAlert.due_date >= due_after)
    
    # Order by due date (most urgent first)
    query = query.order_by(models.ComplianceAlert.due_date.asc())
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts

@router.get("/upcoming", response_model=List[schemas.ComplianceAlert])
async def get_upcoming_alerts(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    now = datetime.utcnow()
    end_date = now + timedelta(days=days)
    
    alerts = db.query(models.ComplianceAlert).filter(
        models.ComplianceAlert.due_date >= now,
        models.ComplianceAlert.due_date <= end_date
    ).order_by(models.ComplianceAlert.due_date.asc()).all()
    
    return alerts

@router.get("/{alert_id}", response_model=schemas.ComplianceAlert)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    alert = db.query(models.ComplianceAlert).filter(models.ComplianceAlert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/", response_model=schemas.ComplianceAlert)
async def create_alert(
    alert: schemas.ComplianceAlertCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    # Check if regulation exists
    regulation = db.query(models.Regulation).filter(models.Regulation.id == alert.regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    db_alert = models.ComplianceAlert(
        title=alert.title,
        description=alert.description,
        due_date=alert.due_date,
        priority=alert.priority,
        regulation_id=alert.regulation_id
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.put("/{alert_id}", response_model=schemas.ComplianceAlert)
async def update_alert(
    alert_id: str,
    alert: schemas.ComplianceAlertCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_alert = db.query(models.ComplianceAlert).filter(models.ComplianceAlert.id == alert_id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if regulation exists
    regulation = db.query(models.Regulation).filter(models.Regulation.id == alert.regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulation not found")
    
    db_alert.title = alert.title
    db_alert.description = alert.description
    db_alert.due_date = alert.due_date
    db_alert.priority = alert.priority
    db_alert.regulation_id = alert.regulation_id
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_admin_user)
):
    db_alert = db.query(models.ComplianceAlert).filter(models.ComplianceAlert.id == alert_id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted successfully"}