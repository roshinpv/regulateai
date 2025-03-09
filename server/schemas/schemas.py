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

    @classmethod
    def from_orm(cls, obj):
        # Extract categories from RegulationCategoryAssociation objects
        if hasattr(obj, 'categories'):
            obj.categories = [
                RegulationCategory(category=assoc.category)
                for assoc in obj.categories
            ]
        return super().from_orm(obj)

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

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

# Document Upload schemas
class DocumentUploadBase(BaseModel):
    title: str
    description: Optional[str] = None
    regulation_id: Optional[str] = None
    jurisdiction_id: Optional[str] = None

class DocumentUploadCreate(DocumentUploadBase):
    file_path: Optional[str] = None
    url: Optional[str] = None
    content_type: str

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