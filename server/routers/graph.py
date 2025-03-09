from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import models
from ..schemas import schemas
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=schemas.GraphData)
async def get_graph_data(
    include_regulations: bool = True,
    include_agencies: bool = True,
    include_banks: bool = True,
    regulation_id: Optional[str] = None,
    agency_id: Optional[str] = None,
    bank_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    nodes = []
    links = []
    
    # Add regulation nodes
    if include_regulations:
        regulations_query = db.query(models.Regulation)
        if regulation_id:
            regulations_query = regulations_query.filter(models.Regulation.id == regulation_id)
        regulations = regulations_query.all()
        
        for reg in regulations:
            nodes.append({
                "id": reg.id,
                "label": reg.title,
                "type": "regulation"
            })
    
    # Add agency nodes
    if include_agencies:
        agencies_query = db.query(models.Agency)
        if agency_id:
            agencies_query = agencies_query.filter(models.Agency.id == agency_id)
        agencies = agencies_query.all()
        
        for agency in agencies:
            nodes.append({
                "id": agency.id,
                "label": agency.name,
                "type": "agency"
            })
    
    # Add bank nodes
    if include_banks:
        banks_query = db.query(models.Bank)
        if bank_id:
            banks_query = banks_query.filter(models.Bank.id == bank_id)
        banks = banks_query.all()
        
        for bank in banks:
            nodes.append({
                "id": bank.id,
                "label": bank.name,
                "type": "bank"
            })
    
    # Add links between agencies and regulations
    if include_agencies and include_regulations:
        agency_reg_links = db.query(models.Regulation, models.Agency).join(
            models.Agency, models.Regulation.agency_id == models.Agency.id
        )
        
        if regulation_id:
            agency_reg_links = agency_reg_links.filter(models.Regulation.id == regulation_id)
        if agency_id:
            agency_reg_links = agency_reg_links.filter(models.Agency.id == agency_id)
        
        for reg, agency in agency_reg_links:
            links.append({
                "source": agency.id,
                "target": reg.id,
                "label": "Issues"
            })
    
    # Add links between regulations and banks
    if include_regulations and include_banks:
        for bank in db.query(models.Bank).all():
            if bank_id and bank.id != bank_id:
                continue
                
            for reg in bank.affected_regulations:
                if regulation_id and reg.id != regulation_id:
                    continue
                    
                links.append({
                    "source": reg.id,
                    "target": bank.id,
                    "label": "Affects"
                })
    
    return {"nodes": nodes, "links": links}

@router.get("/expand/{node_id}", response_model=schemas.GraphData)
async def expand_node(
    node_id: str,
    node_type: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    nodes = []
    links = []
    
    if node_type == "regulation":
        # Get the regulation
        regulation = db.query(models.Regulation).filter(models.Regulation.id == node_id).first()
        if not regulation:
            raise HTTPException(status_code=404, detail="Regulation not found")
        
        # Add regulation node
        nodes.append({
            "id": regulation.id,
            "label": regulation.title,
            "type": "regulation"
        })
        
        # Add agency node and link
        agency = db.query(models.Agency).filter(models.Agency.id == regulation.agency_id).first()
        if agency:
            nodes.append({
                "id": agency.id,
                "label": agency.name,
                "type": "agency"
            })
            links.append({
                "source": agency.id,
                "target": regulation.id,
                "label": "Issues"
            })
        
        # Add bank nodes and links
        for bank in regulation.affected_banks:
            nodes.append({
                "id": bank.id,
                "label": bank.name,
                "type": "bank"
            })
            links.append({
                "source": regulation.id,
                "target": bank.id,
                "label": "Affects"
            })
    
    elif node_type == "agency":
        # Get the agency
        agency = db.query(models.Agency).filter(models.Agency.id == node_id).first()
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Add agency node
        nodes.append({
            "id": agency.id,
            "label": agency.name,
            "type": "agency"
        })
        
        # Add regulation nodes and links
        for regulation in agency.regulations:
            nodes.append({
                "id": regulation.id,
                "label": regulation.title,
                "type": "regulation"
            })
            links.append({
                "source": agency.id,
                "target": regulation.id,
                "label": "Issues"
            })
    
    elif node_type == "bank":
        # Get the bank
        bank = db.query(models.Bank).filter(models.Bank.id == node_id).first()
        if not bank:
            raise HTTPException(status_code=404, detail="Bank not found")
        
        # Add bank node
        nodes.append({
            "id": bank.id,
            "label": bank.name,
            "type": "bank"
        })
        
        # Add regulation nodes and links
        for regulation in bank.affected_regulations:
            nodes.append({
                "id": regulation.id,
                "label": regulation.title,
                "type": "regulation"
            })
            links.append({
                "source": regulation.id,
                "target": bank.id,
                "label": "Affects"
            })
            
            # Add agency nodes and links
            agency = db.query(models.Agency).filter(models.Agency.id == regulation.agency_id).first()
            if agency:
                nodes.append({
                    "id": agency.id,
                    "label": agency.name,
                    "type": "agency"
                })
                links.append({
                    "source": agency.id,
                    "target": regulation.id,
                    "label": "Issues"
                })
    
    else:
        raise HTTPException(status_code=400, detail="Invalid node type")
    
    return {"nodes": nodes, "links": links}