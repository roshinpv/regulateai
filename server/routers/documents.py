from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
import uuid

from ..database import get_db, SessionLocal
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user, get_admin_user
from ..llm.document_processor import document_processor
from ..llm.database_updater import DatabaseUpdater

router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def process_document_task(
        document_id: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        regulation_id: Optional[str] = None,
        jurisdiction_id: Optional[str] = None,
        db: Session = None
):
    """Background task to process a document and add it to the vector store."""
    try:
        # Create a new session if not provided
        if db is None:
            db = SessionLocal()

        # Get document
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            print(f"Document {document_id} not found")
            return

        # Prepare metadata
        metadata = {
            "title": document.title,
            "description": document.description,
            "regulation_id": regulation_id,
            "jurisdiction_id": jurisdiction_id,
            "content_type": document.content_type,
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None
        }

        # Process document and get LLM response
        success, llm_response = await document_processor.process_document(
            document_id=document_id,
            file_path=file_path,
            url=url,
            metadata=metadata
        )

        if success and llm_response:
            # Update database based on LLM response
            try:
                updater = DatabaseUpdater(db)
                update_results = updater.update_from_llm_response(llm_response)

                if not update_results["success"]:
                    print(f"Error updating database from LLM response: {update_results['errors']}")
                else:
                    print(f"Successfully updated database from LLM response: {update_results['updates']}")
            except Exception as e:
                print(f"Error processing LLM response: {str(e)}")

        # Update document status
        document.processed = success
        document.processed_at = datetime.utcnow()

        db.commit()

        print(f"Document {document_id} processed successfully: {success}")

    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


@router.get("/", response_model=List[schemas.DocumentUpload])
async def get_documents(
        skip: int = 0,
        limit: int = 100,
        regulation_id: Optional[str] = None,
        jurisdiction_id: Optional[str] = None,
        processed: Optional[bool] = None,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    query = db.query(models.Document)

    if regulation_id:
        query = query.filter(models.Document.regulation_id == regulation_id)

    if jurisdiction_id:
        query = query.filter(models.Document.jurisdiction_id == jurisdiction_id)

    if processed is not None:
        query = query.filter(models.Document.processed == processed)

    # Order by upload date (most recent first)
    query = query.order_by(models.Document.uploaded_at.desc())

    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=schemas.DocumentUpload)
async def get_document(
        document_id: str,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/upload-file", response_model=schemas.DocumentUpload)
async def upload_document_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        title: str = Form(...),
        description: Optional[str] = Form(None),
        regulation_id: Optional[str] = Form(None),
        jurisdiction_id: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    # Validate regulation if provided
    if regulation_id:
        regulation = db.query(models.Regulation).filter(models.Regulation.id == regulation_id).first()
        if not regulation:
            raise HTTPException(status_code=404, detail="Regulation not found")

    # Validate jurisdiction if provided
    if jurisdiction_id:
        jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == jurisdiction_id).first()
        if not jurisdiction:
            raise HTTPException(status_code=404, detail="Jurisdiction not found")

    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        file.file.close()

    # Create document record
    db_document = models.Document(
        title=title,
        description=description,
        file_path=file_path,
        content_type=file.content_type or "application/octet-stream",
        regulation_id=regulation_id,
        jurisdiction_id=jurisdiction_id,
        user_id=current_user.id
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process document in background
    background_tasks.add_task(
        process_document_task,
        document_id=db_document.id,
        file_path=file_path,
        regulation_id=regulation_id,
        jurisdiction_id=jurisdiction_id,
        db=db
    )

    return db_document


@router.post("/upload-url", response_model=schemas.DocumentUpload)
async def upload_document_url(
        document: schemas.DocumentUploadCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    # Validate URL
    if not document.url:
        raise HTTPException(status_code=400, detail="URL is required")

    # Validate regulation if provided
    if document.regulation_id:
        regulation = db.query(models.Regulation).filter(models.Regulation.id == document.regulation_id).first()
        if not regulation:
            raise HTTPException(status_code=404, detail="Regulation not found")

    # Validate jurisdiction if provided
    if document.jurisdiction_id:
        jurisdiction = db.query(models.Jurisdiction).filter(models.Jurisdiction.id == document.jurisdiction_id).first()
        if not jurisdiction:
            raise HTTPException(status_code=404, detail="Jurisdiction not found")

    # Create document record
    db_document = models.Document(
        title=document.title,
        description=document.description,
        url=document.url,
        content_type=document.content_type,
        regulation_id=document.regulation_id,
        jurisdiction_id=document.jurisdiction_id,
        user_id=current_user.id
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Process document in background
    background_tasks.add_task(
        process_document_task,
        document_id=db_document.id,
        url=document.url,
        regulation_id=document.regulation_id,
        jurisdiction_id=document.jurisdiction_id,
        db=db
    )

    return db_document


@router.put("/{document_id}", response_model=schemas.DocumentUpload)
async def update_document(
        document_id: str,
        document: schemas.DocumentUploadCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_admin_user)
):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update fields
    db_document.title = document.title
    db_document.description = document.description
    db_document.regulation_id = document.regulation_id
    db_document.jurisdiction_id = document.jurisdiction_id

    # Only update URL if it's provided and document is URL-based
    if document.url and db_document.url:
        db_document.url = document.url

    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/{document_id}")
async def delete_document(
        document_id: str,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_admin_user)
):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete document from vector store
    document_processor.delete_document(document_id)

    # If document has a file, delete it
    if db_document.file_path and os.path.exists(db_document.file_path):
        try:
            os.remove(db_document.file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting file {db_document.file_path}: {str(e)}")

    db.delete(db_document)
    db.commit()
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/process", response_model=schemas.DocumentUpload)
async def process_document(
        document_id: str,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_admin_user)
):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Process document in background
    background_tasks.add_task(
        process_document_task,
        document_id=db_document.id,
        file_path=db_document.file_path,
        url=db_document.url,
        regulation_id=db_document.regulation_id,
        jurisdiction_id=db_document.jurisdiction_id,
        db=db
    )

    return db_document


@router.post("/process-batch", response_model=List[schemas.DocumentUpload])
async def process_documents_batch(
        document_ids: List[str],
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_admin_user)
):
    # Get all documents
    documents = db.query(models.Document).filter(models.Document.id.in_(document_ids)).all()

    # Check if all documents exist
    if len(documents) != len(document_ids):
        raise HTTPException(status_code=404, detail="One or more documents not found")

    # Process all documents in background
    for document in documents:
        background_tasks.add_task(
            process_document_task,
            document_id=document.id,
            file_path=document.file_path,
            url=document.url,
            regulation_id=document.regulation_id,
            jurisdiction_id=document.jurisdiction_id,
            db=db
        )

    return documents