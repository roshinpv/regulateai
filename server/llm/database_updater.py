from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..models import models
from ..database import SessionLocal

logger = logging.getLogger(__name__)

class DatabaseUpdater:
    """Handles database updates from LLM responses."""
    
    def __init__(self, db: Session):
        self.db = db
        self._regulation_cache = {}  # Cache for regulation lookups
        self.WELLS_FARGO_ID = "bank-001"  # Fixed ID for Wells Fargo
    
    def _parse_categories(self, category_str: str) -> List[models.RegulationCategory]:
        """
        Parse a category string into a list of RegulationCategory enums.
        Handles compound categories and maps them to the correct enum values.
        
        Args:
            category_str: Category string from LLM response
            
        Returns:
            List of RegulationCategory enum values
        """
        # Split on common delimiters
        delimiters = ['&', 'and', ',', ';']
        parts = category_str.strip()
        for delimiter in delimiters:
            parts = ' '.join(parts.split(delimiter))
        categories = [part.strip() for part in parts.split()]
        
        # Map to known categories
        category_mapping = {
            'financial': models.RegulationCategory.FINANCIAL,
            'regulation': models.RegulationCategory.FINANCIAL,
            'regulatory': models.RegulationCategory.FINANCIAL,
            'consumer': models.RegulationCategory.CONSUMER_PROTECTION,
            'protection': models.RegulationCategory.CONSUMER_PROTECTION,
            'risk': models.RegulationCategory.RISK,
            'management': models.RegulationCategory.RISK,
            'capital': models.RegulationCategory.CAPITAL,
            'liquidity': models.RegulationCategory.CAPITAL,
            'fraud': models.RegulationCategory.FRAUD,
            'privacy': models.RegulationCategory.DATA_PRIVACY,
            'data': models.RegulationCategory.DATA_PRIVACY,
            'aml': models.RegulationCategory.AML,
            'laundering': models.RegulationCategory.AML,
            'reporting': models.RegulationCategory.REPORTING,
            'governance': models.RegulationCategory.GOVERNANCE,
            'market': models.RegulationCategory.MARKET_CONDUCT,
            'conduct': models.RegulationCategory.MARKET_CONDUCT,
            'cyber': models.RegulationCategory.CYBERSECURITY,
            'security': models.RegulationCategory.CYBERSECURITY,
            'operational': models.RegulationCategory.OPERATIONAL,
            'operations': models.RegulationCategory.OPERATIONAL
        }
        
        result_categories = set()
        for part in categories:
            part_lower = part.lower()
            # Try to match each word to a category
            for word in part_lower.split():
                if word in category_mapping:
                    result_categories.add(category_mapping[word])
        
        # If no categories were matched, use OTHER
        if not result_categories:
            result_categories.add(models.RegulationCategory.OTHER)
        
        return list(result_categories)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        Handles special values and various date formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None
            
        # Handle special values
        special_values = {
            "ongoing": None,
            "continuous": None,
            "not specified": None,
            "tbd": None,
            "to be determined": None,
            "n/a": None,
            "none": None,
        }
        
        if date_str.lower() in special_values:
            return special_values[date_str.lower()]
        
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",  # 2024-03-15
            "%Y/%m/%d",  # 2024/03/15
            "%d-%m-%Y",  # 15-03-2024
            "%d/%m/%Y",  # 15/03/2024
            "%B %d, %Y", # March 15, 2024
            "%b %d, %Y", # Mar 15, 2024
            "%Y-%m",     # 2024-03 (assumes first of month)
            "%Y",        # 2024 (assumes January 1st)
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _get_regulation(self, regulation_id: str) -> Optional[models.Regulation]:
        """
        Get a regulation by ID, using cache to avoid repeated queries.
        
        Args:
            regulation_id: ID of the regulation to find
            
        Returns:
            Regulation model or None if not found
        """
        # Check cache first
        if regulation_id in self._regulation_cache:
            return self._regulation_cache[regulation_id]
        
        # Query database and update cache
        regulation = self.db.query(models.Regulation).filter_by(id=regulation_id).first()
        if regulation:
            self._regulation_cache[regulation_id] = regulation
        return regulation
    
    def _get_wells_fargo(self) -> Optional[models.Bank]:
        """Get the Wells Fargo bank entity."""
        return self.db.query(models.Bank).filter_by(id=self.WELLS_FARGO_ID).first()
    
    def update_from_llm_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates database tables based on LLM response data.
        
        Args:
            data: Dictionary containing the LLM response data
            
        Returns:
            Dictionary with update results
        """
        try:
            results = {
                "success": True,
                "updates": {
                    "jurisdictions": [],
                    "agencies": [],
                    "regulations": [],
                    "compliance_steps": [],
                    "risk_mappings": [],
                    "related_regulations": [],
                    "bank_associations": []
                },
                "errors": []
            }
            
            # Clear regulation cache
            self._regulation_cache = {}
            
            # Get Wells Fargo bank
            wells_fargo = self._get_wells_fargo()
            if not wells_fargo:
                results["errors"].append("Wells Fargo bank not found in database")
                return results
            
            # Process in order of dependencies
            if "jurisdictions" in data:
                self._process_jurisdictions(data["jurisdictions"], results)
                self.db.flush()  # Ensure jurisdictions are saved
            
            if "agencies" in data:
                self._process_agencies(data["agencies"], results)
                self.db.flush()  # Ensure agencies are saved
            
            if "regulations" in data:
                self._process_regulations(data["regulations"], results, wells_fargo)
                self.db.flush()  # Ensure regulations are saved
            
            if "compliance_steps" in data:
                self._process_compliance_steps(data["compliance_steps"], results)
                self.db.flush()
            
            if "risk_compliance_mapping" in data:
                self._process_risk_mappings(data["risk_compliance_mapping"], results)
                self.db.flush()
            
            if "related_regulations" in data:
                self._process_related_regulations(data["related_regulations"], results)
                self.db.flush()
            
            self.db.commit()
            return results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating database from LLM response: {str(e)}")
            results["success"] = False
            results["errors"].append(str(e))
            return results
    
    def _process_jurisdictions(self, jurisdictions: List[Dict[str, Any]], results: Dict[str, Any]):
        """Process jurisdiction updates."""
        for jur_data in jurisdictions:
            try:
                # First try to find by ID
                jurisdiction = self.db.query(models.Jurisdiction).filter_by(id=jur_data["id"]).first()
                
                # If not found by ID, try to find by code (which should be unique)
                if not jurisdiction:
                    jurisdiction = self.db.query(models.Jurisdiction).filter_by(code=jur_data["code"]).first()
                
                if jurisdiction:
                    # Update existing jurisdiction
                    jurisdiction.name = jur_data["name"]
                    jurisdiction.code = jur_data["code"]
                    jurisdiction.type = jur_data["type"]
                    results["updates"]["jurisdictions"].append(f"Updated: {jur_data['id']}")
                else:
                    # Create new jurisdiction
                    jurisdiction = models.Jurisdiction(
                        id=jur_data["id"],
                        name=jur_data["name"],
                        code=jur_data["code"],
                        type=jur_data["type"]
                    )
                    self.db.add(jurisdiction)
                    results["updates"]["jurisdictions"].append(f"Created: {jur_data['id']}")
                
            except Exception as e:
                results["errors"].append(f"Error processing jurisdiction {jur_data.get('id')}: {str(e)}")
    
    def _process_agencies(self, agencies: List[Dict[str, Any]], results: Dict[str, Any]):
        """Process agency updates."""
        for agency_data in agencies:
            try:
                # First try to find by ID
                agency = self.db.query(models.Agency).filter_by(id=agency_data["id"]).first()
                
                # If not found by ID, try to find by name
                if not agency:
                    agency = self.db.query(models.Agency).filter_by(name=agency_data["name"]).first()
                
                if agency:
                    # Update existing agency
                    agency.description = agency_data["description"]
                    agency.website = agency_data.get("website")
                    
                    # Only update name if it's different and not already taken
                    if agency.name != agency_data["name"]:
                        existing_with_name = self.db.query(models.Agency).filter_by(name=agency_data["name"]).first()
                        if not existing_with_name:
                            agency.name = agency_data["name"]
                    
                    results["updates"]["agencies"].append(f"Updated: {agency_data['id']}")
                else:
                    # Check if an agency with this name already exists
                    existing_agency = self.db.query(models.Agency).filter_by(name=agency_data["name"]).first()
                    if existing_agency:
                        # Log that we're skipping this agency due to name conflict
                        results["updates"]["agencies"].append(
                            f"Skipped: {agency_data['id']} (name '{agency_data['name']}' already exists)"
                        )
                        continue
                    
                    # Create new agency
                    agency = models.Agency(
                        id=agency_data["id"],
                        name=agency_data["name"],
                        description=agency_data["description"],
                        website=agency_data.get("website")
                    )
                    self.db.add(agency)
                    results["updates"]["agencies"].append(f"Created: {agency_data['id']}")
                
                # Commit after each agency to catch any integrity errors early
                self.db.flush()
                
            except IntegrityError as e:
                self.db.rollback()
                results["errors"].append(
                    f"Integrity error processing agency {agency_data.get('id')}: Agency name must be unique"
                )
            except Exception as e:
                results["errors"].append(f"Error processing agency {agency_data.get('id')}: {str(e)}")
    
    def _process_regulations(self, regulations: List[Dict[str, Any]], results: Dict[str, Any], wells_fargo: models.Bank):
        """Process regulation updates."""
        for reg_data in regulations:
            try:
                regulation = self.db.query(models.Regulation).filter_by(id=reg_data["id"]).first()
                
                # Parse dates with flexible format handling
                effective_date = self._parse_date(reg_data.get("effective_date"))
                compliance_deadline = self._parse_date(reg_data.get("compliance_deadline"))
                last_updated = self._parse_date(reg_data.get("last_updated")) or datetime.utcnow()
                
                # Parse categories
                categories = self._parse_categories(reg_data["category"])
                
                if regulation:
                    # Update existing regulation
                    regulation.title = reg_data["title"]
                    regulation.agency_id = reg_data["agency_id"]
                    regulation.jurisdiction_id = reg_data.get("jurisdiction_id")
                    regulation.impact_level = reg_data["impact_level"]
                    regulation.last_updated = last_updated
                    regulation.summary = reg_data["summary"]
                    regulation.effective_date = effective_date
                    regulation.compliance_deadline = compliance_deadline
                    regulation.source_url = reg_data.get("source_url")
                    regulation.official_reference = reg_data.get("official_reference")
                    
                    # Update categories
                    regulation.categories = []
                    for category in categories:
                        cat_assoc = models.RegulationCategoryAssociation(
                            regulation_id=regulation.id,
                            category=category
                        )
                        regulation.categories.append(cat_assoc)
                    
                    # Ensure Wells Fargo association
                    if wells_fargo not in regulation.affected_banks:
                        regulation.affected_banks.append(wells_fargo)
                        results["updates"]["bank_associations"].append(
                            f"Associated: {reg_data['id']} -> Wells Fargo"
                        )
                    
                    results["updates"]["regulations"].append(f"Updated: {reg_data['id']}")
                else:
                    # Create new regulation
                    regulation = models.Regulation(
                        id=reg_data["id"],
                        title=reg_data["title"],
                        agency_id=reg_data["agency_id"],
                        jurisdiction_id=reg_data.get("jurisdiction_id"),
                        impact_level=reg_data["impact_level"],
                        last_updated=last_updated,
                        summary=reg_data["summary"],
                        effective_date=effective_date,
                        compliance_deadline=compliance_deadline,
                        source_url=reg_data.get("source_url"),
                        official_reference=reg_data.get("official_reference")
                    )
                    
                    # Add categories
                    for category in categories:
                        cat_assoc = models.RegulationCategoryAssociation(
                            regulation_id=regulation.id,
                            category=category
                        )
                        regulation.categories.append(cat_assoc)
                    
                    # Associate with Wells Fargo
                    regulation.affected_banks.append(wells_fargo)
                    results["updates"]["bank_associations"].append(
                        f"Associated: {reg_data['id']} -> Wells Fargo"
                    )
                    
                    self.db.add(regulation)
                    results["updates"]["regulations"].append(f"Created: {reg_data['id']}")
                
                # Add to cache
                self._regulation_cache[reg_data["id"]] = regulation
                
            except Exception as e:
                results["errors"].append(f"Error processing regulation {reg_data.get('id')}: {str(e)}")
    
    def _process_compliance_steps(self, steps: List[Dict[str, Any]], results: Dict[str, Any]):
        """Process compliance step updates."""
        for step_data in steps:
            try:
                step = self.db.query(models.ComplianceStep).filter_by(id=step_data["id"]).first()
                
                if step:
                    # Update existing step
                    step.regulation_id = step_data["regulation_id"]
                    step.description = step_data["description"]
                    step.order = step_data["order"]
                    results["updates"]["compliance_steps"].append(f"Updated: {step_data['id']}")
                else:
                    # Create new step
                    step = models.ComplianceStep(
                        id=step_data["id"],
                        regulation_id=step_data["regulation_id"],
                        description=step_data["description"],
                        order=step_data["order"]
                    )
                    self.db.add(step)
                    results["updates"]["compliance_steps"].append(f"Created: {step_data['id']}")
                
            except Exception as e:
                results["errors"].append(f"Error processing compliance step {step_data.get('id')}: {str(e)}")
    
    def _process_risk_mappings(self, mappings: List[Dict[str, Any]], results: Dict[str, Any]):
        """Process risk compliance mappings."""
        for mapping in mappings:
            try:
                # Use cached regulation lookup
                regulation = self._get_regulation(mapping["regulation_id"])
                if not regulation:
                    logger.error(f"Regulation not found in cache or database: {mapping['regulation_id']}")
                    results["errors"].append(f"Regulation not found: {mapping['regulation_id']}")
                    continue
                
                # Find risk assessment unit by compliance area
                unit = self.db.query(models.RiskAssessmentUnit).filter_by(name=mapping["compliance_area"]).first()
                if not unit:
                    logger.error(f"Risk assessment unit not found: {mapping['compliance_area']}")
                    results["errors"].append(f"Risk assessment unit not found: {mapping['compliance_area']}")
                    continue
                
                # Add unit to regulation if not already mapped
                if unit not in regulation.responsible_units:
                    regulation.responsible_units.append(unit)
                    results["updates"]["risk_mappings"].append(
                        f"Mapped: {mapping['regulation_id']} -> {mapping['compliance_area']}"
                    )
                    logger.info(f"Successfully mapped regulation {mapping['regulation_id']} to unit {mapping['compliance_area']}")
                
            except Exception as e:
                logger.error(f"Error processing risk mapping: {str(e)}")
                results["errors"].append(f"Error processing risk mapping: {str(e)}")
    
    def _process_related_regulations(self, relations: List[Dict[str, Any]], results: Dict[str, Any]):
        """Process related regulation mappings."""
        for relation in relations:
            try:
                # Use cached regulation lookups
                regulation = self._get_regulation(relation["regulation_id"])
                related_regulation = self._get_regulation(relation["related_regulation_id"])
                
                if not regulation or not related_regulation:
                    results["errors"].append(f"One or both regulations not found: {relation}")
                    continue
                
                # Add bidirectional relationship if not exists
                if related_regulation not in regulation.related_regulations:
                    regulation.related_regulations.append(related_regulation)
                    results["updates"]["related_regulations"].append(
                        f"Related: {relation['regulation_id']} <-> {relation['related_regulation_id']}"
                    )
                
            except Exception as e:
                results["errors"].append(f"Error processing related regulations: {str(e)}")