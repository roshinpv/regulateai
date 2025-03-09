from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base

# Association tables for many-to-many relationships
regulation_entity = Table(
    "regulation_entity",
    Base.metadata,
    Column("regulation_id", String, ForeignKey("regulations.id")),
    Column("entity_name", String),
)

bank_regulation = Table(
    "bank_regulation",
    Base.metadata,
    Column("bank_id", String, ForeignKey("banks.id")),
    Column("regulation_id", String, ForeignKey("regulations.id")),
)

regulation_unit = Table(
    "regulation_unit",
    Base.metadata,
    Column("regulation_id", String, ForeignKey("regulations.id")),
    Column("unit_id", String, ForeignKey("risk_assessment_units.id")),
)


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


class ImpactLevel(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


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


class RegulationCategoryAssociation(Base):
    __tablename__ = "regulation_categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_id = Column(String, ForeignKey("regulations.id"))
    category = Column(Enum(RegulationCategory))

    # Relationship back to regulation
    regulation = relationship("Regulation", back_populates="categories")


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    agency_id = Column(String, ForeignKey("agencies.id"))
    jurisdiction_id = Column(String, ForeignKey("jurisdictions.id"), nullable=True)
    impact_level = Column(Enum(ImpactLevel), default=ImpactLevel.MEDIUM)
    last_updated = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text)
    effective_date = Column(DateTime, nullable=True)
    compliance_deadline = Column(DateTime, nullable=True)
    source_url = Column(String, nullable=True)
    official_reference = Column(String, nullable=True)

    # Relationships
    agency = relationship("Agency", back_populates="regulations")
    jurisdiction = relationship("Jurisdiction", back_populates="regulations", foreign_keys=[jurisdiction_id])
    compliance_steps = relationship("ComplianceStep", back_populates="regulation", cascade="all, delete-orphan")
    affected_banks = relationship("Bank", secondary=bank_regulation, back_populates="affected_regulations")
    updates = relationship("RegulatoryUpdate", back_populates="regulation", cascade="all, delete-orphan")
    alerts = relationship("ComplianceAlert", back_populates="regulation", cascade="all, delete-orphan")
    responsible_units = relationship(
        "RiskAssessmentUnit",
        secondary=regulation_unit,
        back_populates="regulations"
    )
    related_regulations = relationship(
        "Regulation",
        secondary=Table(
            "related_regulations",
            Base.metadata,
            Column("regulation_id", String, ForeignKey("regulations.id"), primary_key=True),
            Column("related_regulation_id", String, ForeignKey("regulations.id"), primary_key=True)
        ),
        primaryjoin="Regulation.id==related_regulations.c.regulation_id",
        secondaryjoin="Regulation.id==related_regulations.c.related_regulation_id",
        backref="referenced_by"
    )
    documents = relationship("Document", back_populates="regulation")
    categories = relationship(
        "RegulationCategoryAssociation",
        back_populates="regulation",
        cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    code = Column(String, index=True)
    type = Column(Enum(JurisdictionType), default=JurisdictionType.NATIONAL)
    parent_id = Column(String, ForeignKey("jurisdictions.id"), nullable=True)

    # Relationships
    parent = relationship("Jurisdiction", remote_side=[id], backref="sub_jurisdictions")
    regulations = relationship("Regulation", back_populates="jurisdiction")


class RiskAssessmentUnit(Base):
    __tablename__ = "risk_assessment_units"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    category = Column(Enum(UnitCategory))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    regulations = relationship(
        "Regulation",
        secondary=regulation_unit,
        back_populates="responsible_units"
    )


class ComplianceStep(Base):
    __tablename__ = "compliance_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    regulation_id = Column(String, ForeignKey("regulations.id"))
    description = Column(Text)
    order = Column(Integer)

    # Relationships
    regulation = relationship("Regulation", back_populates="compliance_steps")


class Agency(Base):
    __tablename__ = "agencies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    jurisdiction_id = Column(String, ForeignKey("jurisdictions.id"), nullable=True)
    website = Column(String, nullable=True)

    # Relationships
    regulations = relationship("Regulation", back_populates="agency")
    jurisdiction = relationship("Jurisdiction")


class Bank(Base):
    __tablename__ = "banks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    jurisdiction_id = Column(String, ForeignKey("jurisdictions.id"), nullable=True)
    size_category = Column(String, nullable=True)  # e.g., "Global Systemically Important", "Regional", etc.

    # Relationships
    affected_regulations = relationship("Regulation", secondary=bank_regulation, back_populates="affected_banks")
    jurisdiction = relationship("Jurisdiction")


class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(Enum(ImpactLevel), default=ImpactLevel.MEDIUM)
    regulation_id = Column(String, ForeignKey("regulations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    regulation = relationship("Regulation", back_populates="alerts")


class RegulatoryUpdate(Base):
    __tablename__ = "regulatory_updates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    agency = Column(String)
    description = Column(Text)
    regulation_id = Column(String, ForeignKey("regulations.id"))

    # Relationships
    regulation = relationship("Regulation", back_populates="updates")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text)
    sender = Column(String)  # 'user' or 'bot'
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"))


class Citation(Base):
    __tablename__ = "citations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("chat_messages.id"))
    regulation_id = Column(String, ForeignKey("regulations.id"))
    text = Column(Text)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    url = Column(String, nullable=True)
    content_type = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    regulation_id = Column(String, ForeignKey("regulations.id"), nullable=True)
    jurisdiction_id = Column(String, ForeignKey("jurisdictions.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"))

    # Relationships
    regulation = relationship("Regulation", back_populates="documents")
    jurisdiction = relationship("Jurisdiction")
    user = relationship("User")