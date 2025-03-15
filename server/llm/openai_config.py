from pydantic_settings import BaseSettings
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OpenAISettings(BaseSettings):
    """OpenAI configuration settings."""
    
    # API configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Generation parameters
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TOP_P: float = 0.95
    OPENAI_FREQUENCY_PENALTY: float = 0.0
    OPENAI_PRESENCE_PENALTY: float = 0.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def load_settings() -> OpenAISettings:
    """
    Load OpenAI settings from environment variables.
    
    Returns:
        OpenAISettings: Configuration settings
    """
    try:
        settings = OpenAISettings()
        
        # Override settings from environment variables
        settings.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        settings.OPENAI_MODEL = os.environ.get("OPENAI_MODEL", settings.OPENAI_MODEL)
        settings.OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", settings.OPENAI_TEMPERATURE))
        settings.OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", settings.OPENAI_MAX_TOKENS))
        settings.OPENAI_TOP_P = float(os.environ.get("OPENAI_TOP_P", settings.OPENAI_TOP_P))
        settings.OPENAI_FREQUENCY_PENALTY = float(os.environ.get("OPENAI_FREQUENCY_PENALTY", settings.OPENAI_FREQUENCY_PENALTY))
        settings.OPENAI_PRESENCE_PENALTY = float(os.environ.get("OPENAI_PRESENCE_PENALTY", settings.OPENAI_PRESENCE_PENALTY))
        
        return settings
    except Exception as e:
        logger.error(f"Error loading OpenAI settings: {str(e)}")
        return OpenAISettings()

# Create settings instance
settings = load_settings()

def validate_api_key() -> bool:
    """
    Validate that the OpenAI API key is configured.
    
    Returns:
        bool: True if API key is configured, False otherwise
    """
    api_key = settings.OPENAI_API_KEY
    
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return False
        
    if api_key == "your-api-key-here":
        logger.error("OpenAI API key has default placeholder value")
        return False
    
    return True