# Regulatory Compliance Platform

A comprehensive platform for managing regulatory compliance in the financial sector, featuring a local LLM-powered assistant and RAG implementation.

## Features

- Regulatory knowledge base management
- Document upload and processing
- Local LLM integration with Llama 3
- Retrieval-Augmented Generation (RAG) for intelligent responses
- Interactive knowledge graph visualization
- Compliance alerts and tracking

## Setup

### Prerequisites

- Node.js 18+
- Python 3.10+
- At least 8GB RAM (16GB recommended)
- GPU with 8GB+ VRAM (optional, for faster LLM inference)

### Installation

1. Clone the repository
2. Install Node.js dependencies:
   ```
   npm install
   ```
3. Install Python dependencies:
   ```
   pip install -r server/requirements.txt
   ```

### Download LLM Model

The application uses Llama 3 for local inference. Download the model:

```
python server/llm/download_model.py
```

This will download the Llama 3 8B Instruct quantized model (approximately 4.8GB) to the `models` directory.

### Running the Application

1. Start the backend server:
   ```
   npm run server
   ```

2. Start the frontend development server:
   ```
   npm run dev
   ```

3. Access the application at http://localhost:5173

## Usage

### Document Processing

1. Navigate to Settings > Upload Documents
2. Upload regulatory documents (PDF, DOCX, TXT) or import from URLs
3. Process the documents to add them to the knowledge base

### AI Assistant

The AI assistant uses the processed documents to provide accurate responses to regulatory compliance questions. It combines:

- Local LLM inference with Llama 3
- Vector search with ChromaDB
- Retrieval-Augmented Generation (RAG) for context-aware responses

### Knowledge Graph

Explore the relationships between regulations, agencies, banks, and jurisdictions through the interactive knowledge graph visualization.

## Architecture

The application uses a modern stack:

- Frontend: React, TypeScript, Tailwind CSS
- Backend: FastAPI (Python)
- LLM: Llama 3 with llama-cpp-python
- Vector Database: ChromaDB
- Embeddings: Sentence Transformers
- Document Processing: LangChain

## License

MIT