from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

from .config import settings

logger = logging.getLogger(__name__)

class EmbeddingManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.embeddings = None
        self.text_splitter = None
        self.initialized = False
        
        # Initialize embeddings
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize the embedding model."""
        try:
            # Initialize HuggingFace embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs={'device': 'cuda' if self._is_cuda_available() else 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                is_separator_regex=False,
            )
            
            self.initialized = True
            logger.info(f"Embeddings initialized successfully with model: {self.embedding_model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            return False
    
    def _is_cuda_available(self):
        """Check if CUDA is available for GPU acceleration."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def is_initialized(self):
        """Check if the embeddings are initialized and ready to use."""
        return self.initialized
    
    def get_embeddings(self):
        """Get the embeddings instance."""
        if not self.initialized:
            if not self._initialize_embeddings():
                raise ValueError("Embeddings are not initialized and could not be initialized.")
        return self.embeddings
    
    def get_text_splitter(self):
        """Get the text splitter instance."""
        if not self.initialized:
            if not self._initialize_embeddings():
                raise ValueError("Text splitter is not initialized and could not be initialized.")
        return self.text_splitter
    
    def split_text(self, text):
        """Split text into chunks for embedding."""
        if not self.initialized:
            if not self._initialize_embeddings():
                raise ValueError("Text splitter is not initialized and could not be initialized.")
        
        return self.text_splitter.split_text(text)

# Singleton instance
embedding_manager = EmbeddingManager()