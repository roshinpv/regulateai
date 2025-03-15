from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base

# Existing imports and models...

class TrainingStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class EmployeeTraining(Base):
    __tablename__ = "employee_trainings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_name = Column(String, nullable=False)
    employee_email = Column(String, nullable=False)
    manager_name = Column(String, nullable=False)
    manager_email = Column(String, nullable=False)
    training_name = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "employee_name": self.employee_name,
            "employee_email": self.employee_email,
            "manager_name": self.manager_name,
            "manager_email": self.manager_email,
            "training_name": self.training_name,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "notification_sent": self.notification_sent,
            "notification_sent_at": self.notification_sent_at.isoformat() if self.notification_sent_at else None
        }