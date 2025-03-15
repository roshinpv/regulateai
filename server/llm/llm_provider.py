from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

from .model import llm_manager
from .openai_client import openai_client
from .config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def analyze_document(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze document text to extract structured information."""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response to a prompt."""
        pass

class LocalLLMProvider(LLMProvider):
    """Local LLM provider using Llama."""
    
    def __init__(self):
        self.llm = llm_manager
    
    async def analyze_document(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze document using local LLM."""
        try:
            prompt = f"""Analyze the following regulatory document and extract structured information:

{text}

Extract and organize the information into a JSON object with the following structure:
{{
  "regulations": [
    {{
      "id": "REG-[UUID]",
      "title": "string",
      "agency_id": "AG-[UUID]",
      "impact_level": "High|Medium|Low",
      "summary": "string"
    }}
  ],
  "agencies": [
    {{
      "id": "AG-[UUID]",
      "name": "string",
      "description": "string"
    }}
  ],
  "compliance_steps": [
    {{
      "id": "CS-[UUID]",
      "regulation_id": "REG-[UUID]",
      "description": "string",
      "order": number
    }}
  ]
}}"""

            response = self.llm.generate_response(prompt)
            
            # Parse response as JSON
            try:
                import json
                return json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing document with local LLM: {str(e)}")
            return None
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using local LLM."""
        try:
            return self.llm.generate_response(prompt, context)
        except Exception as e:
            logger.error(f"Error generating response with local LLM: {str(e)}")
            return "Error generating response"

class OpenAIProvider(LLMProvider):
    """OpenAI provider."""
    
    def __init__(self):
        self.client = openai_client
    
    async def analyze_document(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze document using OpenAI."""
        try:
            return await self.client.analyze_document(text)
        except Exception as e:
            logger.error(f"Error analyzing document with OpenAI: {str(e)}")
            return None
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI."""
        try:
            # Format prompt with context if provided
            if context:
                full_prompt = f"""Context:
{context}

Question: {prompt}

Please provide a response based on the context above."""
            else:
                full_prompt = prompt
            
            # Use async client in sync context
            import asyncio
            response = asyncio.run(self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                top_p=settings.OPENAI_TOP_P,
                frequency_penalty=settings.OPENAI_FREQUENCY_PENALTY,
                presence_penalty=settings.OPENAI_PRESENCE_PENALTY
            ))
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return "Error generating response"

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def get_provider() -> LLMProvider:
        """Get the configured LLM provider."""
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured, falling back to local LLM")
                return LocalLLMProvider()
            return OpenAIProvider()
        return LocalLLMProvider()

# Singleton instance
llm_provider = LLMProviderFactory.get_provider()