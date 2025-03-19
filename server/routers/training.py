from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from jinja2 import Template

from ..database import get_db
from ..models.models import EmployeeTraining, TrainingStatus
from ..dependencies import get_current_user, get_admin_user

router = APIRouter()

# Email template for manager notifications
EMAIL_TEMPLATE = """
<html>
<body>
    <h2>Training Compliance Notification</h2>
    <p>Dear {{ manager_name }},</p>
    <p>The following employees under your supervision have pending training requirements:</p>
    
    <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
        <thead>
            <tr style="background-color: #f3f4f6;">
                <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Employee</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Training</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Due Date</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #e5e7eb;">Status</th>
            </tr>
        </thead>
        <tbody>
            {% for training in trainings %}
            <tr>
                <td style="padding: 12px; border: 1px solid #e5e7eb;">
                    {{ training.employee_name }}<br>
                    <span style="color: #6b7280; font-size: 0.875rem;">{{ training.employee_email }}</span>
                </td>
                <td style="padding: 12px; border: 1px solid #e5e7eb;">{{ training.training_name }}</td>
                <td style="padding: 12px; border: 1px solid #e5e7eb;">{{ training.due_date.strftime('%Y-%m-%d') }}</td>
                <td style="padding: 12px; border: 1px solid #e5e7eb;">{{ training.status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <p style="margin-top: 20px;">Please ensure that these trainings are completed by their respective due dates.</p>
    
    <p style="margin-top: 20px;">Best regards,<br>Compliance Team</p>
</body>
</html>
"""

async def send_email_notification(manager_email: str, manager_name: str, trainings: List[EmployeeTraining]):
    """Send email notification to manager about employee trainings."""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Training Compliance Notification'
        msg['From'] = os.getenv('SMTP_FROM_EMAIL', 'compliance@company.com')
        msg['To'] = manager_email

        # Render HTML email
        template = Template(EMAIL_TEMPLATE)
        html = template.render(
            manager_name=manager_name,
            trainings=trainings
        )
        
        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP(os.getenv('SMTP_HOST', 'localhost'), int(os.getenv('SMTP_PORT', 25))) as server:
            if os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'):
                server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error sending email to {manager_email}: {str(e)}")
        return False

@router.post("/send-notifications")
async def send_training_notifications(
    data: Dict[str, List[Dict]],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Send notifications to managers about employee trainings."""
    try:
        manager_groups = data.get("managerGroups", {})
        processed_count = 0
        
        for manager_email, trainings in manager_groups.items():
            # Skip if no trainings for this manager
            if not trainings:
                continue
                
            # Create training records
            for training in trainings:
                db_training = EmployeeTraining(
                    employee_name=training["employeeName"],
                    employee_email=training["employeeEmail"],
                    manager_name=training["managerName"],
                    manager_email=training["managerEmail"],
                    training_name=training["trainingName"],
                    due_date=datetime.fromisoformat(training["dueDate"].replace('Z', '+00:00')),
                    status=TrainingStatus(training["status"])
                )
                db.add(db_training)
            
            # Commit to get IDs
            db.flush()
            
            # Get all trainings for this manager
            manager_trainings = [t for t in trainings if t["managerEmail"] == manager_email]
            
            # Send email in background
            background_tasks.add_task(
                send_email_notification,
                manager_email,
                manager_trainings[0]["managerName"],
                manager_trainings
            )
            
            processed_count += len(manager_trainings)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Successfully processed {processed_count} training records",
            "processed_count": processed_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing training notifications: {str(e)}"
        )

@router.get("/trainings")
async def get_trainings(
    skip: int = 0,
    limit: int = 100,
    status: TrainingStatus = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Get all training records with optional filtering."""
    query = db.query(EmployeeTraining)
    
    if status:
        query = query.filter(EmployeeTraining.status == status)
    
    total = query.count()
    trainings = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "trainings": [training.to_dict() for training in trainings]
    }

@router.put("/trainings/{training_id}/status")
async def update_training_status(
    training_id: str,
    status: TrainingStatus,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Update the status of a training record."""
    training = db.query(EmployeeTraining).filter(EmployeeTraining.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    training.status = status
    training.updated_at = datetime.utcnow()
    
    db.commit()
    
    return training.to_dict()