from langchain_chroma import Chroma
import chromadb
import logging
import os

from .config import settings
from .embeddings import embedding_manager

logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = settings.COLLECTION_NAME
        self.vectorstore = None
        self.initialized = False
        
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize vector store
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize the vector store."""
        try:
            # Get embeddings
            embeddings = embedding_manager.get_embeddings()
            
            # Initialize Chroma client
            client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Initialize or get collection
            self.vectorstore = Chroma(
                client=client,
                collection_name=self.collection_name,
                embedding_function=embeddings,
            )
            
            self.initialized = True
            logger.info(f"Vector store initialized successfully with collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            return False
    
    def is_initialized(self):
        """Check if the vector store is initialized and ready to use."""
        return self.initialized
    
    def get_vectorstore(self):
        """Get the vector store instance."""
        if not self.initialized:
            if not self._initialize_vectorstore():
                raise ValueError("Vector store is not initialized and could not be initialized.")
        return self.vectorstore
    
    def add_texts(self, texts, metadatas=None, ids=None):
        """Add texts to the vector store."""
        if not self.initialized:
            if not self._initialize_vectorstore():
                raise ValueError("Vector store is not initialized and could not be initialized.")
        
        try:
            return self.vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        except Exception as e:
            logger.error(f"Error adding texts to vector store: {str(e)}")
            raise
    
    def similarity_search(self, query, k=None, filter=None):
        """Search for similar documents in the vector store."""
        if not self.initialized:
            if not self._initialize_vectorstore():
                raise ValueError("Vector store is not initialized and could not be initialized.")
        
        try:
            k = k or settings.NUM_RESULTS
            return self.vectorstore.similarity_search(query=query, k=k, filter=filter)
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def similarity_search_with_score(self, query, k=None, filter=None):
        """Search for similar documents with relevance scores."""
        if not self.initialized:
            if not self._initialize_vectorstore():
                raise ValueError("Vector store is not initialized and could not be initialized.")
        
        try:
            k = k or settings.NUM_RESULTS
            return self.vectorstore.similarity_search_with_score(query=query, k=k, filter=filter)
        except Exception as e:
            logger.error(f"Error searching vector store with scores: {str(e)}")
            return []
    
    def delete(self, ids=None, filter=None):
        """Delete documents from the vector store."""
        if not self.initialized:
            if not self._initialize_vectorstore():
                raise ValueError("Vector store is not initialized and could not be initialized.")
        
        try:
            if ids:
                self.vectorstore._collection.delete(ids=ids)
            elif filter:
                self.vectorstore._collection.delete(where=filter)
            else:
                # Delete all documents
                self.vectorstore._collection.delete()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting from vector store: {str(e)}")
            return False

# Singleton instance
vectorstore_manager = VectorStoreManager()