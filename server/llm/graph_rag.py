import networkx as nx
from typing import List, Dict, Any, Optional, Set
import logging
from datetime import datetime
from sentence_transformers import util
import torch
import json

from .embeddings import embedding_manager
from .vectorstore import vectorstore_manager
from .llm_provider import llm_provider
from .config import settings

logger = logging.getLogger(__name__)

class GraphRAG:
    """Graph-based Retrieval Augmented Generation for processing large documents."""
    
    def __init__(self):
        self.embedding_manager = embedding_manager
        self.vectorstore_manager = vectorstore_manager
        self.graph = nx.DiGraph()
        
    def process_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document using graph-based RAG.
        
        Args:
            text: Document text to process
            metadata: Optional metadata about the document
            
        Returns:
            Dict containing processed information and relationships
        """
        try:
            # Split text into chunks
            chunks = self.embedding_manager.split_text(text)
            
            if not chunks:
                logger.warning("No chunks extracted from text")
                return {}
            
            # Get embeddings for chunks
            embeddings = self.embedding_manager.get_embeddings()
            chunk_embeddings = embeddings.encode(chunks, convert_to_tensor=True)
            
            # Calculate similarity matrix
            similarity_matrix = util.pytorch_cos_sim(chunk_embeddings, chunk_embeddings)
            
            # Build graph
            self._build_graph(chunks, similarity_matrix)
            
            # Extract key information using graph analysis
            key_chunks = self._extract_key_chunks()
            
            # Generate summaries and extract relationships
            results = self._analyze_chunks(key_chunks, metadata)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in graph-based RAG processing: {str(e)}")
            return {}
    
    def _build_graph(self, chunks: List[str], similarity_matrix: torch.Tensor):
        """Build a graph from text chunks based on similarity."""
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes (chunks)
        for i, chunk in enumerate(chunks):
            self.graph.add_node(i, text=chunk)
        
        # Add edges based on similarity
        threshold = settings.SIMILARITY_THRESHOLD
        num_chunks = len(chunks)
        
        for i in range(num_chunks):
            for j in range(i + 1, num_chunks):
                similarity = similarity_matrix[i][j].item()
                if similarity >= threshold:
                    self.graph.add_edge(i, j, weight=similarity)
                    self.graph.add_edge(j, i, weight=similarity)
    
    def _extract_key_chunks(self) -> List[str]:
        """Extract key chunks using graph centrality measures."""
        try:
            # Calculate centrality measures
            pagerank = nx.pagerank(self.graph)
            betweenness = nx.betweenness_centrality(self.graph)
            
            # Combine centrality scores
            combined_scores = {}
            for node in self.graph.nodes():
                combined_scores[node] = (
                    pagerank.get(node, 0) * 0.7 +  # Weight pagerank more heavily
                    betweenness.get(node, 0) * 0.3
                )
            
            # Get top chunks based on combined score
            top_nodes = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:settings.NUM_RESULTS]
            
            # Get text of top chunks
            key_chunks = [
                self.graph.nodes[node]["text"]
                for node, _ in top_nodes
            ]
            
            return key_chunks
            
        except Exception as e:
            logger.error(f"Error extracting key chunks: {str(e)}")
            return []
    
    def _analyze_chunks(
        self, 
        chunks: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze key chunks to extract structured information."""
        try:
            # Combine chunks with metadata for context
            context = "\n\n".join(chunks)
            if metadata:
                context += f"\n\nDocument Metadata:\n{json.dumps(metadata, indent=2)}"
            
            # Generate structured analysis using configured LLM provider
            prompt = f"""Analyze the following regulatory document excerpts and extract key information:

Context:
{context}

Extract and organize the information into a structured format including:
1. Regulations mentioned
2. Regulatory agencies involved
3. Compliance requirements
4. Key dates and deadlines
5. Related regulations and relationships
6. Risk assessment areas

Provide the analysis in a clear, structured format."""

            response = llm_provider.generate_response(prompt)
            
            # Store analysis in vector store for future retrieval
            self.vectorstore_manager.add_texts(
                texts=[response],
                metadatas=[{
                    "type": "analysis",
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }]
            )
            
            return {
                "analysis": response,
                "key_excerpts": chunks,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error analyzing chunks: {str(e)}")
            return {
                "analysis": "Error analyzing document",
                "key_excerpts": chunks,
                "metadata": metadata
            }
    
    def query(self, question: str, context_size: int = 3) -> Dict[str, Any]:
        """
        Query the processed documents using graph-based retrieval.
        
        Args:
            question: User's question
            context_size: Number of related chunks to include in context
            
        Returns:
            Dict containing answer and supporting information
        """
        try:
            # Get question embedding
            embeddings = self.embedding_manager.get_embeddings()
            question_embedding = embeddings.encode(question, convert_to_tensor=True)
            
            # Find most relevant chunks
            relevant_chunks = []
            for node in self.graph.nodes():
                chunk = self.graph.nodes[node]["text"]
                chunk_embedding = embeddings.encode(chunk, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(question_embedding, chunk_embedding).item()
                relevant_chunks.append((node, similarity))
            
            # Sort by similarity
            relevant_chunks.sort(key=lambda x: x[1], reverse=True)
            
            # Get top chunk and its neighbors
            context_chunks = set()
            if relevant_chunks:
                top_node = relevant_chunks[0][0]
                context_chunks.add(self.graph.nodes[top_node]["text"])
                
                # Add neighboring chunks
                neighbors = list(self.graph.neighbors(top_node))
                neighbors.sort(
                    key=lambda n: self.graph[top_node][n]["weight"],
                    reverse=True
                )
                
                for neighbor in neighbors[:context_size - 1]:
                    context_chunks.add(self.graph.nodes[neighbor]["text"])
            
            # Generate answer using context
            context = "\n\n".join(context_chunks)
            prompt = f"""Answer the following question using the provided context:

Context:
{context}

Question: {question}

Provide a clear, accurate answer based on the context. If the context doesn't contain relevant information, say so."""

            answer = llm_provider.generate_response(prompt, context)
            
            return {
                "answer": answer,
                "context": list(context_chunks),
                "confidence": relevant_chunks[0][1] if relevant_chunks else 0
            }
            
        except Exception as e:
            logger.error(f"Error in graph-based query: {str(e)}")
            return {
                "answer": "Error processing question",
                "context": [],
                "confidence": 0
            }

# Singleton instance
graph_rag = GraphRAG()