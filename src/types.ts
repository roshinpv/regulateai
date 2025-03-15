// Types for the application

export interface Regulation {
  id: string;
  title: string;
  agency_id: string;
  agency?: {
    id: string;
    name: string;
  };
  jurisdiction_id?: string;
  jurisdiction?: Jurisdiction;
  impact_level: 'High' | 'Medium' | 'Low';
  last_updated: string;
  summary: string;
  categories: RegulationCategory[];
  effective_date?: string;
  compliance_deadline?: string;
  source_url?: string;
  official_reference?: string;
  compliance_steps: ComplianceStep[];
  affected_banks?: Bank[];
  updates?: RegulatoryUpdate[];
  alerts?: ComplianceAlert[];
  related_regulations?: Regulation[];
  responsible_units?: RiskAssessmentUnit[];
}

export interface ComplianceStep {
  id: string;
  regulation_id: string;
  description: string;
  order: number;
}

export interface Agency {
  id: string;
  name: string;
  description: string;
  jurisdiction_id?: string;
  jurisdiction?: Jurisdiction;
  website?: string;
  regulations?: Regulation[];
}

export interface Jurisdiction {
  id: string;
  name: string;
  code: string;
  type: 'Global' | 'Regional' | 'National' | 'State/Province' | 'Local';
  parent_id?: string;
  parent?: Jurisdiction;
  sub_jurisdictions?: Jurisdiction[];
}

export interface Bank {
  id: string;
  name: string;
  jurisdiction_id?: string;
  jurisdiction?: Jurisdiction;
  size_category?: string;
  affected_regulations?: Regulation[];
}

export interface ComplianceAlert {
  id: string;
  title: string;
  description: string;
  due_date: string;
  priority: 'High' | 'Medium' | 'Low';
  regulation_id: string;
  regulation?: Regulation;
  created_at: string;
}

export interface RegulatoryUpdate {
  id: string;
  title: string;
  date: string;
  agency: string;
  description: string;
  regulation_id: string;
  regulation?: Regulation;
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'regulation' | 'agency' | 'bank' | 'jurisdiction';
}

export interface GraphLink {
  source: string;
  target: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: string;
  user_id: string;
  citations?: {
    id?: string;
    regulation_id: string;
    text: string;
  }[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Document {
  id: string;
  title: string;
  description?: string;
  file_path?: string;
  url?: string;
  content_type: string;
  uploaded_at: string;
  processed: boolean;
  processed_at?: string;
  regulation_id?: string;
  jurisdiction_id?: string;
  user_id: string;
}

export interface RiskAssessmentUnit {
  id: string;
  name: string;
  description: string;
  category: 'Application' | 'Infrastructure' | 'Security' | 'Governance' | 'Operations';
  created_at?: string;
  updated_at?: string;
  regulations?: Regulation[];
}

export interface RegulationCategory {
  id?: string;
  regulation_id?: string;
  category: RegulationCategoryType;
}

export type RegulationCategoryType = 
  | 'Risk Management'
  | 'Capital & Liquidity'
  | 'Consumer Protection'
  | 'Financial Regulation'
  | 'Fraud Prevention'
  | 'Data Privacy'
  | 'Anti-Money Laundering'
  | 'Financial Reporting'
  | 'Corporate Governance'
  | 'Market Conduct'
  | 'Cybersecurity'
  | 'Operational Risk'
  | 'Other';

export type ImpactLevel = 'High' | 'Medium' | 'Low';

export type JurisdictionType = 'Global' | 'Regional' | 'National' | 'State/Province' | 'Local';

export type UnitCategory = 'Application' | 'Infrastructure' | 'Security' | 'Governance' | 'Operations';

export interface LLMResponse {
  regulations: {
    id: string;
    title: string;
    agency_id: string;
    jurisdiction_id?: string;
    impact_level: ImpactLevel;
    last_updated: string;
    summary: string;
    category: string;
    effective_date?: string;
    compliance_deadline?: string;
    source_url?: string;
    official_reference?: string;
  }[];
  agencies: {
    id: string;
    name: string;
    description: string;
    website?: string;
  }[];
  jurisdictions: {
    id: string;
    name: string;
    code: string;
    type: JurisdictionType;
  }[];
  compliance_steps: {
    id: string;
    regulation_id: string;
    description: string;
    order: number;
  }[];
  risk_compliance_mapping: {
    regulation_id: string;
    compliance_area: string;
  }[];
  related_regulations: {
    regulation_id: string;
    related_regulation_id: string;
  }[];
}