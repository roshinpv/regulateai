from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user
from ..llm.rag import rag_engine

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=schemas.AssistantResponse)
async def query_assistant(
    query: schemas.AssistantQuery,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Log the query
    logger.info(f"User {query.user_id} asked: {query.query}")
    
    # Save user message to database
    user_message = models.ChatMessage(
        content=query.query,
        sender="user",
        user_id=query.user_id
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    try:
        # Generate response using RAG
        response, sources = rag_engine.answer_question(query.query)
        
        # Save bot message to database
        bot_message = models.ChatMessage(
            content=response,
            sender="bot",
            user_id=query.user_id
        )
        db.add(bot_message)
        db.commit()
        db.refresh(bot_message)
        
        # Save citations
        db_citations = []
        for source in sources:
            if 'document_id' in source:
                # Find the regulation associated with this document
                document = db.query(models.Document).filter(models.Document.id == source.get('document_id').split('-chunk-')[0]).first()
                
                if document and document.regulation_id:
                    citation_text = f"Source: {source.get('title', 'Document')}"
                    
                    db_citation = models.Citation(
                        message_id=bot_message.id,
                        regulation_id=document.regulation_id,
                        text=citation_text
                    )
                    db.add(db_citation)
                    db_citations.append({
                        "regulation_id": document.regulation_id,
                        "text": citation_text
                    })
        
        db.commit()
        
        return {
            "response": response,
            "citations": db_citations
        }
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        
        # Fallback response
        fallback_response = "I'm sorry, but I encountered an error while processing your request. Please try again later."
        
        # Save fallback bot message to database
        bot_message = models.ChatMessage(
            content=fallback_response,
            sender="bot",
            user_id=query.user_id
        )
        db.add(bot_message)
        db.commit()
        
        return {
            "response": fallback_response,
            "citations": []
        }

@router.get("/history/{user_id}", response_model=List[schemas.ChatMessage])
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Ensure the user is requesting their own history or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this chat history"
        )
    
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == user_id
    ).order_by(models.ChatMessage.timestamp.desc()).limit(limit).all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    # Get citations for bot messages
    for message in messages:
        if message.sender == "bot":
            citations = db.query(models.Citation).filter(
                models.Citation.message_id == message.id
            ).all()
            message.citations = citations
    
    return messages

@router.delete("/history/{user_id}")
async def clear_chat_history(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Ensure the user is clearing their own history or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to clear this chat history"
        )
    
    # Delete all messages for this user
    db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == user_id
    ).delete()
    
    db.commit()
    
    return {"message": "Chat history cleared successfully"}