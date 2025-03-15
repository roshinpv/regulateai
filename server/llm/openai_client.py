from typing import Dict, Any, Optional
import json
from openai import OpenAI, AsyncOpenAI
import logging
import asyncio
from contextlib import asynccontextmanager

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
        self._client_lock = asyncio.Lock()
        
        # Initialize client if API key is configured
        if validate_api_key():
            try:
                # Initialize async client
                self.client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.client is not None
    
    @asynccontextmanager
    async def get_client(self):
        """Get the OpenAI client with proper cleanup."""
        if not self.is_available():
            raise ValueError("OpenAI client not available")
            
        async with self._client_lock:
            try:
                yield self.client
            finally:
                # Ensure proper cleanup
                if hasattr(self.client, 'close'):
                    await self.client.close()
                elif hasattr(self.client.http_client, 'aclose'):
                    await self.client.http_client.aclose()
    
    async def analyze_document(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze document text using OpenAI to extract regulatory information.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Dict containing structured regulatory data or None if analysis fails
        """
        if not self.is_available():
            logger.error("OpenAI client not available")
            return None
        
        try:
            # Prepare the system message with output format instructions
            system_message = """You are a regulatory compliance expert. Analyze the provided document and extract structured information about regulations, agencies, jurisdictions, compliance steps, and risk assessment mappings.

Your response should be a JSON object with the following structure:
{
  "regulations": [
    {
      "id": "REG-[UUID]",
      "title": "string",
      "agency_id": "AG-[UUID]",
      "jurisdiction_id": "JUR-[UUID]",
      "impact_level": "High|Medium|Low",
      "last_updated": "YYYY-MM-DD",
      "summary": "string",
      "category": "string",
      "effective_date": "YYYY-MM-DD",
      "compliance_deadline": "YYYY-MM-DD",
      "source_url": "string",
      "official_reference": "string"
    }
  ],
  "agencies": [
    {
      "id": "AG-[UUID]",
      "name": "string",
      "description": "string",
      "website": "string"
    }
  ],
  "jurisdictions": [
    {
      "id": "JUR-[UUID]",
      "name": "string",
      "code": "string",
      "type": "Global|Regional|National|State|Local"
    }
  ],
  "compliance_steps": [
    {
      "id": "CS-[UUID]",
      "regulation_id": "REG-[UUID]",
      "description": "string",
      "order": number
    }
  ],
  "risk_compliance_mapping": [
    {
      "regulation_id": "REG-[UUID]",
      "compliance_area": "string"
    }
  ],
  "related_regulations": [
    {
      "regulation_id": "REG-[UUID]",
      "related_regulation_id": "REG-[UUID]"
    }
  ]
}"""
            
            async with self.get_client() as client:
                # Create chat completion
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": text}
                    ],
                    temperature=settings.OPENAI_TEMPERATURE,
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    top_p=settings.OPENAI_TOP_P,
                    frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                    presence_penalty=settings.OPENAI_PRESENCE_PENALTY,
                    response_format={"type": "json_object"}
                )
                
                # Extract and parse the JSON response
                if response.choices and response.choices[0].message.content:
                    try:
                        return json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing OpenAI response as JSON: {str(e)}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing document with OpenAI: {str(e)}")
            return None

# Singleton instance
openai_client = OpenAIClient()