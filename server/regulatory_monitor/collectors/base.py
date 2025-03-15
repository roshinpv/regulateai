from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UpdateCollector(ABC):
    """Base class for regulatory update collectors."""
    
    def __init__(self, agency_id: str, config: Dict[str, Any]):
        self.agency_id = agency_id
        self.config = config
    
    @abstractmethod
    async def collect_updates(self) -> List[Dict[str, Any]]:
        """Collect regulatory updates from the source."""
        pass
    
    def format_update(
        self,
        title: str,
        content: str,
        update_type: str,
        published_date: datetime,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format a regulatory update into a standard structure."""
        return {
            "agency_id": self.agency_id,
            "title": title,
            "content": content,
            "update_type": update_type,
            "published_date": published_date.isoformat(),
            "url": url,
            "metadata": metadata or {},
            "collected_at": datetime.utcnow().isoformat()
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common HTML entities
        replacements = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.strip()