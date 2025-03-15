from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case, text
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user

router = APIRouter()

def calculate_compliance_score(db: Session, bank_id: str) -> float:
    """
    Calculate compliance score for a bank based on multiple factors:
    - Completed compliance steps
    - Risk assessment coverage
    - Alert status
    - Document processing status
    - Regulatory update implementation
    """
    try:
        # Get total regulations affecting the bank
        total_regs = db.query(models.Regulation).join(
            models.bank_regulation,
            models.Regulation.id == models.bank_regulation.c.regulation_id
        ).filter(
            models.bank_regulation.c.bank_id == bank_id
        ).count()
        
        if total_regs == 0:
            return 0.0
        
        # Calculate weights for different factors
        weights = {
            'compliance_steps': 0.3,
            'risk_coverage': 0.2,
            'alerts': 0.2,
            'documents': 0.15,
            'updates': 0.15
        }
        
        scores = {}
        
        # 1. Compliance Steps Score
        total_steps = db.query(models.ComplianceStep).join(
            models.Regulation,
            models.ComplianceStep.regulation_id == models.Regulation.id
        ).join(
            models.bank_regulation,
            models.Regulation.id == models.bank_regulation.c.regulation_id
        ).filter(
            models.bank_regulation.c.bank_id == bank_id
        ).count()
        
        # For demo, assume 75% steps completed
        completed_steps = int(total_steps * 0.75)
        scores['compliance_steps'] = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        # 2. Risk Assessment Coverage Score
        total_units = db.query(models.RiskAssessmentUnit).count()
        covered_units = db.query(models.RiskAssessmentUnit).join(
            models.regulation_unit
        ).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank_id
        ).distinct().count()
        
        scores['risk_coverage'] = (covered_units / total_units * 100) if total_units > 0 else 0
        
        # 3. Alerts Score (inverse - fewer high priority alerts is better)
        total_alerts = db.query(models.ComplianceAlert).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank_id
        ).count()
        
        high_priority_alerts = db.query(models.ComplianceAlert).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank_id,
            models.ComplianceAlert.priority == 'High'
        ).count()
        
        scores['alerts'] = 100 - ((high_priority_alerts / total_alerts * 100) if total_alerts > 0 else 0)
        
        # 4. Document Processing Score
        total_docs = db.query(models.Document).filter(
            models.Document.regulation_id.in_(
                db.query(models.Regulation.id).join(
                    models.bank_regulation
                ).filter(
                    models.bank_regulation.c.bank_id == bank_id
                )
            )
        ).count()
        
        processed_docs = db.query(models.Document).filter(
            models.Document.regulation_id.in_(
                db.query(models.Regulation.id).join(
                    models.bank_regulation
                ).filter(
                    models.bank_regulation.c.bank_id == bank_id
                )
            ),
            models.Document.processed == True
        ).count()
        
        scores['documents'] = (processed_docs / total_docs * 100) if total_docs > 0 else 0
        
        # 5. Regulatory Updates Score
        month_ago = datetime.utcnow() - timedelta(days=30)
        total_updates = db.query(models.RegulatoryUpdate).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank_id,
            models.RegulatoryUpdate.date >= month_ago
        ).count()
        
        # For demo, assume 80% updates implemented
        implemented_updates = int(total_updates * 0.8)
        scores['updates'] = (implemented_updates / total_updates * 100) if total_updates > 0 else 0
        
        # Calculate weighted average
        final_score = sum(score * weights[factor] for factor, score in scores.items())
        
        return round(final_score, 1)
        
    except Exception as e:
        print(f"Error calculating compliance score: {str(e)}")
        return 0.0

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard statistics."""
    try:
        # Get Wells Fargo bank
        bank = db.query(models.Bank).filter_by(id="bank-001").first()
        if not bank:
            raise HTTPException(status_code=404, detail="Bank not found")
        
        # Calculate compliance score
        compliance_score = calculate_compliance_score(db, bank.id)
        
        # Get pending alerts count and high priority alerts
        alerts = db.query(models.ComplianceAlert).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank.id,
            models.ComplianceAlert.due_date >= datetime.utcnow()
        ).all()
        
        pending_alerts = len(alerts)
        high_priority_alerts = sum(1 for alert in alerts if alert.priority == 'High')
        
        # Get active regulations count
        active_regulations = db.query(models.Regulation).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank.id
        ).count()
        
        # Get new regulations in last 30 days
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_regulations = db.query(models.Regulation).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank.id,
            models.Regulation.last_updated >= month_ago
        ).count()
        
        # Get recent updates count
        recent_updates = db.query(models.RegulatoryUpdate).join(
            models.Regulation
        ).join(
            models.bank_regulation
        ).filter(
            models.bank_regulation.c.bank_id == bank.id,
            models.RegulatoryUpdate.date >= month_ago
        ).count()
        
        return {
            "pendingAlerts": pending_alerts,
            "highPriorityAlerts": high_priority_alerts,
            "activeRegulations": active_regulations,
            "newRegulations": new_regulations,
            "recentUpdates": recent_updates,
            "complianceScore": compliance_score
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )