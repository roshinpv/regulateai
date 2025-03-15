from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import asyncio

from .config import settings

logger = logging.getLogger(__name__)

class AlertManager:
    """Manager for regulatory change alerts."""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
    
    async def process_update(self, update: Dict[str, Any]) -> Optional[str]:
        """
        Process a regulatory update and generate an alert if needed.
        
        Args:
            update: Regulatory update data
            
        Returns:
            Alert ID if alert was generated, None otherwise
        """
        try:
            # Convert update type to enum value
            update_type = self._normalize_update_type(update["update_type"])
            
            # Prepare metadata
            metadata = {
                "source": update.get("metadata", {}),
                "original_id": update.get("id"),
                "collector_type": update.get("collector_type"),
                "processed_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate alert using database function
            with self.Session() as session:
                result = session.execute(
                    text("""
                    SELECT generate_regulatory_alert(
                        :title,
                        :content,
                        :agency_id,
                        :update_type::regulatory_update_type,
                        :published_date::timestamptz,
                        :url,
                        :metadata::jsonb
                    )
                    """),
                    {
                        "title": update["title"],
                        "content": update["content"],
                        "agency_id": update["agency_id"],
                        "update_type": update_type,
                        "published_date": update["published_date"],
                        "url": update.get("url"),
                        "metadata": json.dumps(metadata)
                    }
                )
                
                alert_id = result.scalar()
                session.commit()
                
                if alert_id:
                    logger.info(f"Generated alert {alert_id} for update from {update['agency_id']}")
                    return str(alert_id)
                
                return None
                
        except Exception as e:
            logger.error(f"Error generating alert for update: {str(e)}")
            return None
    
    def _normalize_update_type(self, update_type: str) -> str:
        """Normalize update type to match database enum."""
        type_mapping = {
            "rule change": "Rule Change",
            "guidance": "Guidance",
            "advisory": "Advisory",
            "enforcement action": "Enforcement Action",
            "press release": "Press Release",
            "bulletin": "Bulletin",
            "notice": "Notice"
        }
        
        normalized = type_mapping.get(update_type.lower(), "Other")
        return normalized
    
    async def get_pending_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts that need processing."""
        try:
            with self.Session() as session:
                result = session.execute(
                    text("""
                    SELECT *
                    FROM regulatory_alerts
                    WHERE status = 'New'
                    ORDER BY priority DESC, published_date DESC
                    """)
                )
                
                alerts = [dict(row) for row in result]
                return alerts
                
        except Exception as e:
            logger.error(f"Error getting pending alerts: {str(e)}")
            return []
    
    async def update_alert_status(
        self,
        alert_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update alert status and metadata."""
        try:
            with self.Session() as session:
                # Update status and metadata
                session.execute(
                    text("""
                    UPDATE regulatory_alerts
                    SET status = :status::alert_status,
                        metadata = metadata || :metadata::jsonb,
                        processed_at = CASE 
                            WHEN :status = 'Analyzed' THEN now()
                            ELSE processed_at
                        END,
                        notified_at = CASE
                            WHEN :status = 'Notified' THEN now()
                            ELSE notified_at
                        END
                    WHERE id = :alert_id
                    """),
                    {
                        "alert_id": alert_id,
                        "status": status,
                        "metadata": json.dumps(metadata or {})
                    }
                )
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating alert {alert_id}: {str(e)}")
            return False

# Singleton instance
alert_manager = AlertManager()