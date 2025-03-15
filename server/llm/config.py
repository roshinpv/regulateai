from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os

class LLMSettings(BaseSettings):
    # LLM Provider Configuration
    LLM_PROVIDER: Literal['local', 'openai'] = os.getenv("LLM_PROVIDER", "local")
    
    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/llama-3-8b-instruct.Q4_K_M.gguf")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Vector database settings
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "chroma_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "regulatory_documents")
    
    # Document processing settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM generation settings
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    TOP_P: float = float(os.getenv("TOP_P", "0.95"))
    TOP_K: int = int(os.getenv("TOP_K", "40"))
    
    # RAG settings
    NUM_RESULTS: int = int(os.getenv("NUM_RESULTS", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
    OPENAI_TOP_P: float = float(os.getenv("OPENAI_TOP_P", "0.95"))
    OPENAI_FREQUENCY_PENALTY: float = float(os.getenv("OPENAI_FREQUENCY_PENALTY", "0.0"))
    OPENAI_PRESENCE_PENALTY: float = float(os.getenv("OPENAI_PRESENCE_PENALTY", "0.0"))

settings = LLMSettings()