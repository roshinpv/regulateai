import logging
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
import pypdf
import docx2txt
import re

from .embeddings import embedding_manager
from .vectorstore import vectorstore_manager
from .openai_client import openai_client

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents and add them to the vector store."""

    def __init__(self):
        self.embedding_manager = embedding_manager
        self.vectorstore_manager = vectorstore_manager

    def _filter_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter metadata to only include simple types supported by the vector store.

        Args:
            metadata: Original metadata dictionary

        Returns:
            Dict containing only simple type values (str, int, float, bool)
        """
        filtered = {}
        for key, value in metadata.items():
            # Only include non-None simple type values
            if value is not None and isinstance(value, (str, int, float, bool)):
                filtered[key] = value
        return filtered

    async def process_document(
            self,
            document_id: str,
            file_path: Optional[str] = None,
            url: Optional[str] = None,
            content: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Process a document and add it to the vector store.

        Args:
            document_id: Unique identifier for the document
            file_path: Path to the document file (optional)
            url: URL of the document (optional)
            content: Document content as text (optional)
            metadata: Additional metadata for the document

        Returns:
            Tuple containing:
                - bool: True if processing was successful
                - Dict: LLM response data for database updates, or None if processing failed
        """
        try:
            # Extract text from document
            if content:
                text = content
            elif file_path and os.path.exists(file_path):
                text = self._extract_text_from_file(file_path)
            elif url:
                # In a real implementation, this would fetch and process the document from the URL
                # For now, we'll just use a placeholder
                text = f"Document content from URL: {url}"
            else:
                logger.error(f"No content source provided for document {document_id}")
                return False, None

            if not text:
                logger.error(f"Failed to extract text from document {document_id}")
                return False, None

            # Process text with LLM to extract structured data
            llm_response = await self._process_text_with_llm(text)

            # Split text into chunks
            text_splitter = self.embedding_manager.get_text_splitter()
            chunks = text_splitter.split_text(text)

            if not chunks:
                logger.error(f"No text chunks extracted from document {document_id}")
                return False, None

            # Prepare metadata for each chunk
            if not metadata:
                metadata = {}

            # Filter metadata to only include simple types
            base_metadata = self._filter_metadata(metadata)

            chunk_metadatas = []
            chunk_ids = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}-chunk-{i}"
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                chunk_ids.append(chunk_id)
                chunk_metadatas.append(chunk_metadata)

            # Add chunks to vector store
            self.vectorstore_manager.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )



            logger.info(f"Successfully processed document {document_id} with {len(chunks)} chunks")
            return True, llm_response

        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            return False, None

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a file based on its extension."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_text_from_txt(file_path)
            else:
                logger.warning(f"Unsupported file extension: {file_extension}")
                return ""

        except Exception as e:
            logger.error(f"Error extracting text from file {file_path}: {str(e)}")
            return ""

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return ""

    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from a TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {str(e)}")
            return ""

    async def _process_text_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Process text with LLM to extract structured data.

        Uses OpenAI to analyze the document and extract regulatory information
        in a structured format.

        Args:
            text: Document text to analyze

        Returns:
            Dict containing structured data in the format:
            {
                "regulations": [...],
                "agencies": [...],
                "jurisdictions": [...],
                "compliance_steps": [...],
                "risk_compliance_mapping": [...],
                "related_regulations": [...]
            }
        """
        try:
            # Use OpenAI client to analyze document
            llm_response = await openai_client.analyze_document(text)

            if llm_response:
                logger.info("Successfully extracted regulatory information using OpenAI")
                return llm_response
            else:
                logger.warning("OpenAI analysis returned no results")
                return None

        except Exception as e:
            logger.error(f"Error processing text with LLM: {str(e)}")
            return None

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks from the vector store."""
        try:
            # Delete all chunks for this document
            filter_condition = {"document_id": document_id}
            return self.vectorstore_manager.delete(filter=filter_condition)
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False


# Singleton instance
document_processor = DocumentProcessor()