import aiohttp
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from .base import UpdateCollector

logger = logging.getLogger(__name__)

class APICollector(UpdateCollector):
    """Collector for API-based updates."""
    
    async def collect_updates(self) -> List[Dict[str, Any]]:
        """Collect updates from API endpoints."""
        updates = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint_name, endpoint_url in self.config.get("api_endpoints", {}).items():
                try:
                    # Prepare headers
                    headers = self._get_headers(endpoint_name)
                    
                    # Make API request
                    async with session.get(endpoint_url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Process response based on endpoint type
                            endpoint_updates = await self._process_endpoint_data(
                                endpoint_name,
                                data
                            )
                            
                            updates.extend(endpoint_updates)
                        else:
                            logger.error(
                                f"API request failed for {endpoint_url}: "
                                f"Status {response.status}"
                            )
                
                except Exception as e:
                    logger.error(
                        f"Error collecting updates from {endpoint_url}: {str(e)}"
                    )
                    continue
        
        return updates
    
    def _get_headers(self, endpoint_name: str) -> Dict[str, str]:
        """Get headers for API request."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "RegulationMonitor/1.0"
        }
        
        # Add API key if available
        api_key = self.config.get("api_key")
        if api_key:
            if self.agency_id == "SEC":
                headers["X-SEC-API-KEY"] = api_key
            elif self.agency_id == "CFPB":
                headers["X-API-Key"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    async def _process_endpoint_data(
        self,
        endpoint_name: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process API response data based on endpoint type."""
        updates = []
        
        try:
            if self.agency_id == "SEC":
                if endpoint_name == "edgar":
                    updates.extend(self._process_edgar_data(data))
                elif endpoint_name == "rules":
                    updates.extend(self._process_sec_rules_data(data))
            
            elif self.agency_id == "CFPB":
                if endpoint_name == "regulations":
                    updates.extend(self._process_cfpb_regulations(data))
                elif endpoint_name == "enforcement":
                    updates.extend(self._process_cfpb_enforcement(data))
            
            elif self.agency_id == "FederalReserve":
                if endpoint_name == "press_releases":
                    updates.extend(self._process_fed_press_releases(data))
                elif endpoint_name == "supervision":
                    updates.extend(self._process_fed_supervision(data))
            
        except Exception as e:
            logger.error(
                f"Error processing {endpoint_name} data for {self.agency_id}: {str(e)}"
            )
        
        return updates
    
    def _process_edgar_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process SEC EDGAR API data."""
        updates = []
        
        for filing in data.get("filings", []):
            try:
                update = self.format_update(
                    title=f"SEC Filing: {filing.get('form_type', 'Unknown')}",
                    content=filing.get("description", ""),
                    update_type="Securities Filing",
                    published_date=datetime.fromisoformat(filing.get("filing_date")),
                    url=filing.get("filing_url"),
                    metadata={
                        "form_type": filing.get("form_type"),
                        "company_name": filing.get("company_name"),
                        "cik": filing.get("cik"),
                        "file_number": filing.get("file_number")
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing EDGAR filing: {str(e)}")
                continue
        
        return updates
    
    def _process_sec_rules_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process SEC rules data."""
        updates = []
        
        for rule in data.get("rules", []):
            try:
                update = self.format_update(
                    title=rule.get("title", ""),
                    content=rule.get("description", ""),
                    update_type="Rule Change",
                    published_date=datetime.fromisoformat(rule.get("effective_date")),
                    url=rule.get("url"),
                    metadata={
                        "rule_number": rule.get("rule_number"),
                        "category": rule.get("category"),
                        "comment_period_ends": rule.get("comment_period_ends")
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing SEC rule: {str(e)}")
                continue
        
        return updates
    
    def _process_cfpb_regulations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process CFPB regulations data."""
        updates = []
        
        for reg in data.get("regulations", []):
            try:
                update = self.format_update(
                    title=reg.get("title", ""),
                    content=reg.get("summary", ""),
                    update_type="Regulation",
                    published_date=datetime.fromisoformat(reg.get("published_date")),
                    url=reg.get("url"),
                    metadata={
                        "regulation_number": reg.get("regulation_number"),
                        "cfr_title": reg.get("cfr_title"),
                        "cfr_part": reg.get("cfr_part"),
                        "effective_date": reg.get("effective_date")
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing CFPB regulation: {str(e)}")
                continue
        
        return updates
    
    def _process_cfpb_enforcement(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process CFPB enforcement data."""
        updates = []
        
        for action in data.get("actions", []):
            try:
                update = self.format_update(
                    title=action.get("title", ""),
                    content=action.get("description", ""),
                    update_type="Enforcement Action",
                    published_date=datetime.fromisoformat(action.get("date")),
                    url=action.get("url"),
                    metadata={
                        "action_type": action.get("action_type"),
                        "status": action.get("status"),
                        "defendants": action.get("defendants", []),
                        "products": action.get("products", []),
                        "penalty_amount": action.get("penalty_amount")
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing CFPB enforcement action: {str(e)}")
                continue
        
        return updates
    
    def _process_fed_press_releases(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Federal Reserve press releases."""
        updates = []
        
        for release in data.get("press_releases", []):
            try:
                update = self.format_update(
                    title=release.get("title", ""),
                    content=release.get("content", ""),
                    update_type="Press Release",
                    published_date=datetime.fromisoformat(release.get("date")),
                    url=release.get("url"),
                    metadata={
                        "category": release.get("category"),
                        "topics": release.get("topics", [])
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing Fed press release: {str(e)}")
                continue
        
        return updates
    
    def _process_fed_supervision(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Federal Reserve supervision data."""
        updates = []
        
        for item in data.get("supervision_items", []):
            try:
                update = self.format_update(
                    title=item.get("title", ""),
                    content=item.get("description", ""),
                    update_type="Supervision",
                    published_date=datetime.fromisoformat(item.get("date")),
                    url=item.get("url"),
                    metadata={
                        "supervision_type": item.get("type"),
                        "institutions": item.get("institutions", []),
                        "requirements": item.get("requirements", [])
                    }
                )
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error processing Fed supervision item: {str(e)}")
                continue
        
        return updates