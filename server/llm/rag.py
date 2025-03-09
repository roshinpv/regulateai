from typing import List, Dict, Any, Optional, Tuple
import logging

from .model import llm_manager
from .vectorstore import vectorstore_manager
from .config import settings

logger = logging.getLogger(__name__)

class RAGEngine:
    """Retrieval-Augmented Generation engine for answering questions."""
    
    def __init__(self):
        self.llm_manager = llm_manager
        self.vectorstore_manager = vectorstore_manager
    
    def answer_question(self, question: str, filter_metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Answer a question using RAG.
        
        Args:
            question: The question to answer
            filter_metadata: Optional metadata to filter documents by
            
        Returns:
            Tuple containing:
                - The generated answer
                - List of source documents with metadata
        """
        try:
            # Retrieve relevant documents
            docs_with_scores = self.vectorstore_manager.similarity_search_with_score(
                query=question,
                k=settings.NUM_RESULTS,
                filter=filter_metadata
            )
            
            # Filter documents by similarity threshold
            filtered_docs = []
            for doc, score in docs_with_scores:
                # Convert score to similarity (depends on the embedding model)
                # For cosine similarity, higher is better (closer to 1)
                if score >= settings.SIMILARITY_THRESHOLD:
                    filtered_docs.append(doc)
            
            # If no relevant documents found
            if not filtered_docs:
                answer = self.llm_manager.generate_response(
                    prompt=question,
                    context=None
                )
                return answer, []
            
            # Prepare context from retrieved documents
            context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(filtered_docs)])
            
            # Generate answer
            answer = self.llm_manager.generate_response(
                prompt=question,
                context=context
            )
            
            # Prepare source documents with metadata
            sources = []
            for doc in filtered_docs:
                if hasattr(doc, 'metadata'):
                    sources.append(doc.metadata)
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error in RAG answer generation: {str(e)}")
            # Fallback to direct LLM response
            try:
                answer = self.llm_manager.generate_response(question)
                return answer, []
            except Exception as e2:
                logger.error(f"Error in fallback answer generation: {str(e2)}")
                return "I'm sorry, but I encountered an error while processing your request. Please try again later.", []

# Singleton instance
rag_engine = RAGEngine()