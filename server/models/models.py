from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base

# Enums
class JurisdictionType(str, enum.Enum):
    GLOBAL = "Global"
    REGIONAL = "Regional"
    NATIONAL = "National"
    STATE = "State/Province"
    LOCAL = "Local"

class UnitCategory(str, enum.Enum):
    APPLICATION = "Application"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    GOVERNANCE = "Governance"
    OPERATIONS = "Operations"

class ImpactLevel(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RegulationCategory(str, enum.Enum):
    RISK = "Risk Management"
    CAPITAL = "Capital & Liquidity"
    CONSUMER_PROTECTION = "Consumer Protection"
    FINANCIAL = "Financial Regulation"
    FRAUD = "Fraud Prevention"
    DATA_PRIVACY = "Data Privacy"
    AML = "Anti-Money Laundering"
    REPORTING = "Financial Reporting"
    GOVERNANCE = "Corporate Governance"
    MARKET_CONDUCT = "Market Conduct"
    CYBERSECURITY = "Cybersecurity"
    OPERATIONAL = "Operational Risk"
    OTHER = "Other"

class TrainingStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

# Association Tables
bank_regulation = Table(
    'bank_regulation',
    Base.metadata,
    Column('bank_id', String, ForeignKey('banks.id')),
    Column('regulation_id', String, ForeignKey('regulations.id')),
)

regulation_unit = Table(
    'regulation_unit',
    Base.metadata,
    Column('regulation_id', String, ForeignKey('regulations.id')),
    Column('unit_id', String, ForeignKey('risk_assessment_units.id')),
)

related_regulations = Table(
    'related_regulations',
    Base.metadata,
    Column('regulation_id', String, ForeignKey('regulations.id')),
    Column('related_regulation_id', String, ForeignKey('regulations.id')),
)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    chat_messages = relationship("ChatMessage", back_populates="user")
    documents = relationship("Document", back_populates="user")

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    type = Column(Enum(JurisdictionType), nullable=False)
    parent_id = Column(String, ForeignKey('jurisdictions.id'))
    
    # Relationships
    parent = relationship("Jurisdiction", remote_side=[id])
    sub_jurisdictions = relationship("Jurisdiction")
    agencies = relationship("Agency", back_populates="jurisdiction")
    regulations = relationship("Regulation", back_populates="jurisdiction")
    banks = relationship("Bank", back_populates="jurisdiction")

class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    jurisdiction_id = Column(String, ForeignKey('jurisdictions.id'))
    website = Column(String)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="agencies")
    regulations = relationship("Regulation", back_populates="agency")

class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    jurisdiction_id = Column(String, ForeignKey('jurisdictions.id'))
    size_category = Column(String)
    
    # Relationships
    jurisdiction = relationship("Jurisdiction", back_populates="banks")
    affected_regulations = relationship(
        "Regulation",
        secondary=bank_regulation,
        back_populates="affected_banks"
    )

class RiskAssessmentUnit(Base):
    __tablename__ = "risk_assessment_units"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    category = Column(Enum(UnitCategory), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    regulations = relationship(
        "Regulation",
        secondary=regulation_unit,
        back_populates="responsible_units"
    )

class Regulation(Base):
    __tablename__ = "regulations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    agency_id = Column(String, ForeignKey('agencies.id'), nullable=False)
    jurisdiction_id = Column(String, ForeignKey('jurisdictions.id'))
    impact_level = Column(Enum(ImpactLevel), nullable=False)
    last_updated = Column(DateTime, nullable=False)
    summary = Column(Text)
    effective_date = Column(DateTime)
    compliance_deadline = Column(DateTime)
    source_url = Column(String)
    official_reference = Column(String)
    
    # Relationships
    agency = relationship("Agency", back_populates="regulations")
    jurisdiction = relationship("Jurisdiction", back_populates="regulations")
    compliance_steps = relationship("ComplianceStep", back_populates="regulation")
    affected_banks = relationship(
        "Bank",
        secondary=bank_regulation,
        back_populates="affected_regulations"
    )
    updates = relationship("RegulatoryUpdate", back_populates="regulation")
    alerts = relationship("ComplianceAlert", back_populates="regulation")
    responsible_units = relationship(
        "RiskAssessmentUnit",
        secondary=regulation_unit,
        back_populates="regulations"
    )
    categories = relationship("RegulationCategoryAssociation", back_populates="regulation")
    related_regulations = relationship(
        "Regulation",
        secondary=related_regulations,
        primaryjoin=id==related_regulations.c.regulation_id,
        secondaryjoin=id==related_regulations.c.related_regulation_id,
        backref="related_to"
    )

class RegulationCategoryAssociation(Base):
    __tablename__ = "regulation_categories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_id = Column(String, ForeignKey('regulations.id'), nullable=False)
    category = Column(Enum(RegulationCategory), nullable=False)
    
    # Relationships
    regulation = relationship("Regulation", back_populates="categories")

class ComplianceStep(Base):
    __tablename__ = "compliance_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_id = Column(String, ForeignKey('regulations.id'), nullable=False)
    description = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    # Relationships
    regulation = relationship("Regulation", back_populates="compliance_steps")

class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=False)
    priority = Column(Enum(ImpactLevel), nullable=False)
    regulation_id = Column(String, ForeignKey('regulations.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    regulation = relationship("Regulation", back_populates="alerts")

class RegulatoryUpdate(Base):
    __tablename__ = "regulatory_updates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    agency = Column(String, nullable=False)
    description = Column(Text)
    regulation_id = Column(String, ForeignKey('regulations.id'), nullable=False)
    
    # Relationships
    regulation = relationship("Regulation", back_populates="updates")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'bot'
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    citations = relationship("Citation", back_populates="message")

class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey('chat_messages.id'), nullable=False)
    regulation_id = Column(String, ForeignKey('regulations.id'), nullable=False)
    text = Column(Text, nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="citations")
    regulation = relationship("Regulation")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)
    url = Column(String)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    regulation_id = Column(String, ForeignKey('regulations.id'))
    jurisdiction_id = Column(String, ForeignKey('jurisdictions.id'))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    regulation = relationship("Regulation")
    jurisdiction = relationship("Jurisdiction")
    user = relationship("User", back_populates="documents")

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
    notification_sent_at = Column(DateTime)
    
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