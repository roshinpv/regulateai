from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from typing import List, Optional
from dotenv import load_dotenv

from .database import engine, SessionLocal, Base
from .models import models
from .seed import seed_database
from .routers import (
    agencies, alerts, assistant, auth, banks, graph, regulations, 
    updates, jurisdictions, documents, llm, dashboard, training
)
from .llm.openai_config import validate_api_key
from .regulatory_monitor.monitor import regulatory_monitor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Seed the database
seed_database()

# Validate OpenAI configuration
if not validate_api_key():
    logger.warning("OpenAI API key not properly configured. LLM features will be disabled.")

app = FastAPI(
    title="Regulatory Compliance API",
    description="API for the Regulatory Compliance Platform",
    version="0.1.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4173",  # Vite preview
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(regulations.router, prefix="/api/regulations", tags=["Regulations"])
app.include_router(agencies.router, prefix="/api/agencies", tags=["Agencies"])
app.include_router(banks.router, prefix="/api/banks", tags=["Banks"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Compliance Alerts"])
app.include_router(updates.router, prefix="/api/updates", tags=["Regulatory Updates"])
app.include_router(graph.router, prefix="/api/graph", tags=["Knowledge Graph"])
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI Assistant"])
app.include_router(jurisdictions.router, prefix="/api/jurisdictions", tags=["Jurisdictions"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM Integration"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(training.router, prefix="/api/training", tags=["Training Compliance"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Regulatory Compliance API"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "llm_available": validate_api_key()
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Start the regulatory monitoring system."""
    try:
        regulatory_monitor.start_monitoring()
        logger.info("Regulatory monitoring system started")
    except Exception as e:
        logger.error(f"Error starting regulatory monitoring: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the regulatory monitoring system."""
    try:
        regulatory_monitor.stop_monitoring()
        logger.info("Regulatory monitoring system stopped")
    except Exception as e:
        logger.error(f"Error stopping regulatory monitoring: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)