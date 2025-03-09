from typing import Dict, Any, Optional
import openai
import json
import logging

from .openai_config import settings, validate_api_key

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.client = None

        if validate_api_key():
            try:
                # FIX: Use AsyncOpenAI instead of OpenAI
                self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY , base_url=settings.OPENAI_BASE_URL )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.client is not None

    async def analyze_document(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze document text using OpenAI to extract regulatory information.

        Args:
            text: Document text to analyze.

        Returns:
            A dictionary containing structured regulatory data or None if analysis fails.
        """
        if not self.is_available():
            logger.error("OpenAI client not available")
            return None

        try:
            system_message = """

Role:
You are a Regulatory Compliance Expert for Wells Fargo. Your task is to analyze the provided regulatory document and extract structured data relevant to risk and compliance.

Objective:
Generate a comprehensive regulatory data model that captures key compliance aspects, including:

Regulations (titles, agencies, jurisdictions, impact levels, categories, deadlines, etc.)
Agencies (regulatory bodies, jurisdictions, and oversight responsibilities)
Jurisdictions (national or regional applicability)
Compliance Steps (necessary actions for adherence)
Risk & Compliance Mapping (linking regulations to enterprise compliance areas)
Related Regulations (dependencies or overlapping rules)
The extracted data should be structured in a format suitable for database population and provide meaningful insights for risk and compliance leaders.

Input Requirements:
Raw regulatory documents (e.g., laws, mandates, agency guidelines)
Metadata (jurisdiction, regulatory agency, impact level, category, effective date, compliance deadlines)
Key takeaways summarizing the regulation’s intent and coverage
Risk assessment reasoning (explanation of unit assignments)
Risk-to-Compliance Mapping, aligning each regulation to relevant compliance entities

The risk_compliance_mapping should have one or more values from the below list - Do the mapping according to the functionalities as its name indicates.

    Records Adherence
    Application Lifecycle Management
    Enterprise Architecture Service
    Software Development Lifecycle
    Information Protection
    Business Adherence & Regulatory Change Management
    Cloud Platform
    Disaster Recovery Service
    Foundational Automation
    Technology Change Management
    Incident and Problem Management
    Service Asset and Configuration Management
    Workforce Experience Productivity Solutions
    Foundation Hosting Platforms
    Enterprise Data Center Service
    Availability and Service Level Management
    Technology Infrastructure Operations Support
    Identity and Access Management
    Cyber Security Defense and Monitoring
    Infrastructure Vulnerability Management
    Cyber Security Governance
    Patch Management
    Secure Network Services
    Technology Third Party Management Service
    Application Security
    Shared Services Technology Strategy, Change Enablement & Reporting Service
    External File Transfer Services
    Technology Governance
    
    
Output Format:
Your response should be in JSON format with the following structure:


{
  "regulations": [
    {
      "id": "REG-001",
      "title": "System Safeguards for Trading and Market Oversight",
      "agency_id": "AG-001",
      "jurisdiction_id": "JUR-001",
      "impact_level": "High",
      "last_updated": "2018-11-30",
      "summary": "Establishes risk analysis, oversight, disaster recovery, cybersecurity measures, and compliance tracking for trading platforms.",
      "category": "Cybersecurity & Risk Management",
      "effective_date": "2018-12-01",
      "compliance_deadline": "2020-01-01",
      "source_url": "https://www.federalregister.gov/d/2018-24642a",
      "official_reference": "CFTC Part 37.1401"
    }
  ],
  "agencies": [
    {
      "id": "AG-001",
      "name": "Commodity Futures Trading Commission (CFTC)",
      "description": "Regulates the U.S. derivatives markets, including futures, swaps, and options.",
      "jurisdiction": "United States",
      "website": "https://www.cftc.gov/"
    }
  ],
  "jurisdictions": [
    {
      "id": "JUR-001",
      "name": "United States",
      "code": "US",
      "type": "National"
    }
  ],
  "compliance_steps": [
    {
      "id": "CS-001",
      "regulation_id": "REG-001",
      "description": "Conduct annual enterprise risk assessments and submit reports to regulatory agencies.",
      "order": 1
    },
    {
      "id": "CS-002",
      "regulation_id": "REG-001",
      "description": "Implement cybersecurity controls for trade monitoring and compliance.",
      "order": 2
    }
  ],
  "risk_compliance_mapping": [
    {
      "regulation_id": "REG-001",
      "compliance_area": "Enterprise Risk Management"
    },
    {
      "regulation_id": "REG-001",
      "compliance_area": "Cyber Security Governance"
    },
    {
      "regulation_id": "REG-001",
      "compliance_area": "Incident and Problem Management"
    }
  ],
  "related_regulations": [
    {
      "regulation_id": "REG-001",
      "related_regulation_id": "REG-002"
    }
  ]
}



"""

            new_client = openai.AsyncOpenAI(base_url="https://api.deepseek.com",
                                        api_key="")

            response = await new_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"},
                top_p=settings.OPENAI_TOP_P,
                frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                presence_penalty=settings.OPENAI_PRESENCE_PENALTY

            )

            print(response.choices and response.choices[0].message.content)
            if response.choices and response.choices[0].message.content:
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing OpenAI response as JSON: {str(e)}")
                    return None

            return None

        except Exception as e:
            logger.error(f"Error analyzing document with OpenAI: {e}")
            return None


# Singleton instance
openai_client = OpenAIClient()
