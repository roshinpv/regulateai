from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..dependencies import get_admin_user
from ..llm.database_updater import DatabaseUpdater

router = APIRouter()

@router.post("/update-database")
async def update_database_from_llm(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_admin_user)  # Only admins can update database
):
    """
    Update database tables based on LLM response data.
    
    Args:
        data: Dictionary containing the LLM response data structure
        
    Returns:
        Dictionary with update results
    """
    try:
        updater = DatabaseUpdater(db)
        results = updater.update_from_llm_response(data)
        
        if not results["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Error updating database",
                    "errors": results["errors"]
                }
            )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )