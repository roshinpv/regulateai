import { Regulation, Agency, Bank, ComplianceAlert, RegulatoryUpdate, GraphData, ChatMessage } from '../types';

// Mock Regulations
export const regulations: Regulation[] = [
  {
    id: 'reg-001',
    title: 'Basel III',
    agency: 'FDIC',
    impactLevel: 'High',
    lastUpdated: '2024-02-15',
    summary: 'Basel III is a global, voluntary regulatory framework on bank capital adequacy, stress testing, and market liquidity risk.',
    affectedEntities: ['Wells Fargo'],
    complianceSteps: [
      'Maintain minimum CET1 ratio of 4.5%',
      'Implement liquidity coverage ratio (LCR)',
      'Conduct stress tests quarterly',
      'Report capital adequacy to regulators'
    ],
    category: 'Capital'
  },
  {
    id: 'reg-002',
    title: 'Dodd-Frank Act',
    agency: 'OCC',
    impactLevel: 'Medium',
    lastUpdated: '2023-11-10',
    summary: 'The Dodd-Frank Wall Street Reform and Consumer Protection Act is a federal law that regulates the financial industry.',
    affectedEntities: ['Wells Fargo'],
    complianceSteps: [
      'Establish risk committee',
      'Implement whistleblower programs',
      'Conduct annual stress tests',
      'Report to Financial Stability Oversight Council'
    ],
    category: 'Risk'
  },
  {
    id: 'reg-003',
    title: 'Fair Lending Practices',
    agency: 'OCC',
    impactLevel: 'High',
    lastUpdated: '2023-12-05',
    summary: 'Regulations ensuring fair and equal access to credit for all Americans, prohibiting discrimination in lending.',
    affectedEntities: ['Wells Fargo'],
    complianceSteps: [
      'Train staff on fair lending requirements',
      'Implement non-discriminatory lending policies',
      'Conduct regular audits of lending practices',
      'Report lending data to regulators'
    ],
    category: 'Consumer Protection'
  },
  {
    id: 'reg-004',
    title: 'Anti-Money Laundering (AML)',
    agency: 'FinCEN',
    impactLevel: 'High',
    lastUpdated: '2024-03-01',
    summary: 'Regulations requiring financial institutions to detect and prevent money laundering and terrorist financing.',
    affectedEntities: ['Wells Fargo'],
    complianceSteps: [
      'Implement Know Your Customer (KYC) procedures',
      'Monitor transactions for suspicious activity',
      'File Suspicious Activity Reports (SARs)',
      'Conduct regular AML risk assessments'
    ],
    category: 'Fraud'
  },
  {
    id: 'reg-005',
    title: 'Consumer Financial Protection',
    agency: 'CFPB',
    impactLevel: 'Medium',
    lastUpdated: '2024-02-28',
    summary: 'Regulations protecting consumers in their interactions with financial products and services.',
    affectedEntities: ['Wells Fargo'],
    complianceSteps: [
      'Review consumer complaint procedures',
      'Update disclosure documents',
      'Train staff on consumer protection requirements',
      'Conduct regular compliance audits'
    ],
    category: 'Consumer Protection'
  }
];

// Mock Agencies
export const agencies: Agency[] = [
  {
    id: 'agency-001',
    name: 'FDIC',
    description: 'Federal Deposit Insurance Corporation - Insures deposits and examines/supervises financial institutions.',
    regulations: ['reg-001']
  },
  {
    id: 'agency-002',
    name: 'OCC',
    description: 'Office of the Comptroller of the Currency - Charters, regulates, and supervises national banks.',
    regulations: ['reg-002', 'reg-003']
  },
  {
    id: 'agency-003',
    name: 'FinCEN',
    description: 'Financial Crimes Enforcement Network - Safeguards the financial system from illicit use.',
    regulations: ['reg-004']
  },
  {
    id: 'agency-004',
    name: 'CFPB',
    description: 'Consumer Financial Protection Bureau - Protects consumers in the financial sector.',
    regulations: ['reg-005']
  }
];

// Mock Banks
export const banks: Bank[] = [
  {
    id: 'bank-001',
    name: 'Wells Fargo',
    affectedRegulations: ['reg-001', 'reg-002', 'reg-003', 'reg-004', 'reg-005']
  }
];

// Mock Compliance Alerts
export const complianceAlerts: ComplianceAlert[] = [
  {
    id: 'alert-001',
    title: 'Basel III Capital Ratio Reporting Due',
    description: 'Quarterly capital adequacy report must be submitted to FDIC.',
    dueDate: '2024-06-30',
    priority: 'High',
    regulationId: 'reg-001'
  },
  {
    id: 'alert-002',
    title: 'Annual Stress Test Required',
    description: 'Dodd-Frank mandated annual stress test submission deadline approaching.',
    dueDate: '2024-07-15',
    priority: 'Medium',
    regulationId: 'reg-002'
  },
  {
    id: 'alert-003',
    title: 'Fair Lending Compliance Review',
    description: 'Conduct comprehensive review of lending practices and policies.',
    dueDate: '2024-06-10',
    priority: 'High',
    regulationId: 'reg-003'
  },
  {
    id: 'alert-004',
    title: 'AML Risk Assessment Due',
    description: 'Quarterly AML risk assessment and report submission required.',
    dueDate: '2024-06-30',
    priority: 'High',
    regulationId: 'reg-004'
  },
  {
    id: 'alert-005',
    title: 'Consumer Protection Training Update',
    description: 'Staff training on updated consumer protection requirements needed.',
    dueDate: '2024-08-01',
    priority: 'Medium',
    regulationId: 'reg-005'
  }
];

// Mock Regulatory Updates
export const regulatoryUpdates: RegulatoryUpdate[] = [
  {
    id: 'update-001',
    title: 'Basel III Liquidity Requirements Updated',
    date: '2024-05-15',
    agency: 'FDIC',
    description: 'FDIC has issued updated guidance on liquidity coverage ratio calculations.',
    regulationId: 'reg-001'
  },
  {
    id: 'update-002',
    title: 'Dodd-Frank Stress Test Scenarios Released',
    date: '2024-05-10',
    agency: 'FRB',
    description: 'Federal Reserve has released scenarios for 2024 stress tests.',
    regulationId: 'reg-002'
  },
  {
    id: 'update-003',
    title: 'New Fair Lending Examination Procedures',
    date: '2024-04-28',
    agency: 'OCC',
    description: 'OCC releases updated examination procedures for fair lending compliance.',
    regulationId: 'reg-003'
  },
  {
    id: 'update-004',
    title: 'FinCEN Issues New AML Guidance',
    date: '2024-04-20',
    agency: 'FinCEN',
    description: 'New guidance on suspicious activity monitoring and reporting for digital assets.',
    regulationId: 'reg-004'
  },
  {
    id: 'update-005',
    title: 'CFPB Updates Consumer Protection Guidelines',
    date: '2024-05-01',
    agency: 'CFPB',
    description: 'Updated guidelines for consumer financial product disclosures and marketing.',
    regulationId: 'reg-005'
  }
];

// Mock Graph Data
export const graphData: GraphData = {
  nodes: [
    // Regulation nodes
    { id: 'reg-001', label: 'Basel III', type: 'regulation' },
    { id: 'reg-002', label: 'Dodd-Frank Act', type: 'regulation' },
    { id: 'reg-003', label: 'Fair Lending', type: 'regulation' },
    { id: 'reg-004', label: 'AML', type: 'regulation' },
    { id: 'reg-005', label: 'Consumer Protection', type: 'regulation' },
    
    // Agency nodes
    { id: 'agency-001', label: 'FDIC', type: 'agency' },
    { id: 'agency-002', label: 'OCC', type: 'agency' },
    { id: 'agency-003', label: 'FinCEN', type: 'agency' },
    { id: 'agency-004', label: 'CFPB', type: 'agency' },
    
    // Bank node
    { id: 'bank-001', label: 'Wells Fargo', type: 'bank' }
  ],
  links: [
    // Agency to Regulation links
    { source: 'agency-001', target: 'reg-001', label: 'Issues' },
    { source: 'agency-002', target: 'reg-002', label: 'Issues' },
    { source: 'agency-002', target: 'reg-003', label: 'Issues' },
    { source: 'agency-003', target: 'reg-004', label: 'Issues' },
    { source: 'agency-004', target: 'reg-005', label: 'Issues' },
    
    // Regulation to Bank links
    { source: 'reg-001', target: 'bank-001', label: 'Affects' },
    { source: 'reg-002', target: 'bank-001', label: 'Affects' },
    { source: 'reg-003', target: 'bank-001', label: 'Affects' },
    { source: 'reg-004', target: 'bank-001', label: 'Affects' },
    { source: 'reg-005', target: 'bank-001', label: 'Affects' }
  ]
};

// Mock Chat Messages
export const chatMessages: ChatMessage[] = [
  {
    id: 'msg-001',
    content: "What are Wells Fargo's obligations under Basel III?",
    sender: 'user',
    timestamp: '2024-05-20T10:30:00Z'
  },
  {
    id: 'msg-002',
    content: "As a Global Systemically Important Bank (G-SIB), Wells Fargo must maintain a minimum CET1 ratio of 4.5% under Basel III. The bank is required to implement a Liquidity Coverage Ratio (LCR) to ensure sufficient high-quality liquid assets, conduct quarterly stress tests, and report capital adequacy metrics to regulators regularly.",
    sender: 'bot',
    timestamp: '2024-05-20T10:30:05Z',
    citations: [
      {
        regulationId: 'reg-001',
        text: 'Basel III requires implementation of liquidity coverage ratio (LCR)'
      }
    ]
  },
  {
    id: 'msg-003',
    content: "What are our current fair lending requirements?",
    sender: 'user',
    timestamp: '2024-05-20T10:31:00Z'
  },
  {
    id: 'msg-004',
    content: "Wells Fargo must comply with comprehensive fair lending regulations that prohibit discrimination in lending practices. Key requirements include maintaining non-discriminatory lending policies, conducting regular audits of lending practices, providing staff training on fair lending requirements, and submitting regular reports to regulators. The bank must ensure equal access to credit regardless of protected characteristics and maintain robust documentation of lending decisions.",
    sender: 'bot',
    timestamp: '2024-05-20T10:31:05Z',
    citations: [
      {
        regulationId: 'reg-003',
        text: 'Fair Lending Practices requirements for staff training and audits'
      }
    ]
  }
];