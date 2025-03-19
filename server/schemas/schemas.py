from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class RegulationCategory(str, Enum):
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

class ImpactLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class JurisdictionType(str, Enum):
    GLOBAL = "Global"
    REGIONAL = "Regional"
    NATIONAL = "National"
    STATE = "State/Province"
    LOCAL = "Local"

class UnitCategory(str, Enum):
    APPLICATION = "Application"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    GOVERNANCE = "Governance"
    OPERATIONS = "Operations"

class EntityType(str, Enum):
    CORPORATION = "Corporation"
    NON_PROFIT = "Non-Profit"
    SHELL_COMPANY = "Shell Company"
    FINANCIAL_INTERMEDIARY = "Financial Intermediary"
    INDIVIDUAL = "Individual"
    OTHER = "Other"

class SourceType(str, Enum):
    TRANSACTION_DATA = "Transaction Data"
    PUBLIC_RECORDS = "Public Records"
    NEWS_ARTICLES = "News Articles"
    REGULATORY_FILINGS = "Regulatory Filings"
    COURT_RECORDS = "Court Records"
    SANCTIONS_LISTS = "Sanctions Lists"
    CORPORATE_REGISTRIES = "Corporate Registries"
    FINANCIAL_STATEMENTS = "Financial Statements"
    OTHER = "Other"

class VerificationStatus(str, Enum):
    PENDING = "Pending"
    VERIFIED = "Verified"
    DISPUTED = "Disputed"
    INCONCLUSIVE = "Inconclusive"

# Base schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False

class RegulationBase(BaseModel):
    title: str
    agency_id: str
    impact_level: ImpactLevel
    summary: str
    jurisdiction_id: Optional[str] = None
    effective_date: Optional[datetime] = None
    compliance_deadline: Optional[datetime] = None
    source_url: Optional[str] = None
    official_reference: Optional[str] = None

class JurisdictionBase(BaseModel):
    name: str
    code: str
    type: JurisdictionType
    parent_id: Optional[str] = None

class AgencyBase(BaseModel):
    name: str
    description: str
    jurisdiction_id: Optional[str] = None
    website: Optional[str] = None

class BankBase(BaseModel):
    name: str
    jurisdiction_id: Optional[str] = None
    size_category: Optional[str] = None

class ComplianceStepBase(BaseModel):
    description: str
    order: int

class ComplianceAlertBase(BaseModel):
    title: str
    description: str
    due_date: datetime
    priority: ImpactLevel
    regulation_id: str

class RegulatoryUpdateBase(BaseModel):
    title: str
    date: datetime
    agency: str
    description: str
    regulation_id: str

class ChatMessageBase(BaseModel):
    content: str
    sender: str  # 'user' or 'bot'

class CitationBase(BaseModel):
    regulation_id: str
    text: str

class DocumentUploadBase(BaseModel):
    title: str
    description: Optional[str] = None
    regulation_id: Optional[str] = None
    jurisdiction_id: Optional[str] = None

# Create schemas
class UserCreate(UserBase):
    password: str

class JurisdictionCreate(JurisdictionBase):
    pass

class RegulationCreate(RegulationBase):
    categories: List[RegulationCategory]
    compliance_steps: List[ComplianceStepBase] = []
    affected_bank_ids: List[str] = []
    related_regulation_ids: List[str] = []

class AgencyCreate(AgencyBase):
    pass

class BankCreate(BankBase):
    pass

class ComplianceStepCreate(ComplianceStepBase):
    regulation_id: str

class ComplianceAlertCreate(ComplianceAlertBase):
    pass

class RegulatoryUpdateCreate(RegulatoryUpdateBase):
    pass

class ChatMessageCreate(ChatMessageBase):
    user_id: str
    citations: List[CitationBase] = []

class DocumentUploadCreate(DocumentUploadBase):
    file_path: Optional[str] = None
    url: Optional[str] = None
    content_type: str

# Read schemas
class ComplianceStep(ComplianceStepBase):
    id: str
    regulation_id: str

    class Config:
        from_attributes = True

class Citation(CitationBase):
    id: str
    message_id: str

    class Config:
        from_attributes = True

class ChatMessage(ChatMessageBase):
    id: str
    timestamp: datetime
    user_id: str
    citations: List[Citation] = []

    class Config:
        from_attributes = True

class RegulatoryUpdate(RegulatoryUpdateBase):
    id: str

    class Config:
        from_attributes = True

class ComplianceAlert(ComplianceAlertBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Jurisdiction(JurisdictionBase):
    id: str
    sub_jurisdictions: List["Jurisdiction"] = []

    class Config:
        from_attributes = True

class Bank(BankBase):
    id: str
    affected_regulation_ids: List[str] = []

    class Config:
        from_attributes = True

class Agency(AgencyBase):
    id: str
    regulation_ids: List[str] = []

    class Config:
        from_attributes = True

class RegulationCategory(BaseModel):
    category: RegulationCategory

    class Config:
        from_attributes = True

class RiskAssessmentUnit(BaseModel):
    id: str
    name: str
    description: str
    category: UnitCategory
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Regulation(RegulationBase):
    id: str
    last_updated: datetime
    categories: List[RegulationCategory]
    compliance_steps: List[ComplianceStep] = []
    affected_banks: List[Bank] = []
    updates: List[RegulatoryUpdate] = []
    alerts: List[ComplianceAlert] = []
    jurisdiction: Optional[Jurisdiction] = None
    related_regulations: List["Regulation"] = []
    responsible_units: List[RiskAssessmentUnit] = []

    class Config:
        from_attributes = True

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentUpload(DocumentUploadBase):
    id: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    content_type: str
    uploaded_at: datetime
    processed: bool = False
    processed_at: Optional[datetime] = None
    user_id: str

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Graph schemas
class GraphNode(BaseModel):
    id: str
    label: str
    type: str

class GraphLink(BaseModel):
    source: str
    target: str
    label: str

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

# AI Assistant schemas
class AssistantQuery(BaseModel):
    query: str
    user_id: str

class AssistantResponse(BaseModel):
    response: str
    citations: List[Citation] = []

# Entity Analysis Schemas
class EntityBase(BaseModel):
    name: str
    type: EntityType
    registration_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    incorporation_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityCreate(EntityBase):
    pass

class EntityUpdate(EntityBase):
    analysis_status: Optional[VerificationStatus] = None

class Entity(EntityBase):
    id: str
    risk_score: Optional[int] = None
    confidence_score: Optional[int] = None
    last_analyzed_at: Optional[datetime] = None
    analysis_status: VerificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EntitySourceBase(BaseModel):
    source_type: SourceType
    source_url: Optional[str] = None
    source_date: Optional[datetime] = None
    content: Optional[str] = None
    reliability_score: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class EntitySource(EntitySourceBase):
    id: str
    entity_id: str
    verification_status: VerificationStatus
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EntityTransactionBase(BaseModel):
    transaction_date: datetime
    transaction_type: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    counterparty_id: Optional[str] = None
    risk_indicators: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityTransaction(EntityTransactionBase):
    id: str
    entity_id: str
    created_at: datetime
    counterparty: Optional[Entity] = None

    class Config:
        from_attributes = True

class EntityRelationshipBase(BaseModel):
    relationship_type: str
    strength_score: Optional[int] = None
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityRelationship(EntityRelationshipBase):
    id: str
    from_entity_id: str
    to_entity_id: str
    created_at: datetime
    from_entity: Optional[Entity] = None
    to_entity: Optional[Entity] = None

    class Config:
        from_attributes = True

class EntityRiskFactorBase(BaseModel):
    factor_type: str
    factor_value: Optional[str] = None
    risk_contribution: int
    confidence_score: int
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityRiskFactor(EntityRiskFactorBase):
    id: str
    entity_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class EntitySearchResult(BaseModel):
    entity: Entity
    matched_source: Optional[EntitySource] = None
    relevance_score: float