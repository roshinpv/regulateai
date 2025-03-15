from typing import Dict, List, Any, Type
import logging
import asyncio
from datetime import datetime
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import settings
from .collectors.base import UpdateCollector
from .collectors.rss import RSSCollector
from .collectors.api import APICollector
from .collectors.web import WebCollector
from .alert_manager import alert_manager

logger = logging.getLogger(__name__)

class RegulatoryMonitor:
    """Monitor for collecting regulatory updates from various agencies."""
    
    def __init__(self):
        self.collectors: Dict[str, List[UpdateCollector]] = {}
        self.scheduler = AsyncIOScheduler()
        self._initialize_collectors()
    
    def _initialize_collectors(self):
        """Initialize collectors for each agency."""
        for agency_id, config in settings.agencies.items():
            self.collectors[agency_id] = []
            
            # Add RSS collector if RSS feeds are configured
            if config.rss_feeds:
                self.collectors[agency_id].append(
                    RSSCollector(agency_id, config.dict())
                )
            
            # Add API collector if API endpoints are configured
            if config.api_endpoints:
                self.collectors[agency_id].append(
                    APICollector(agency_id, config.dict())
                )
            
            # Add web collector if web scraping URLs are configured
            if config.web_scraping_urls:
                self.collectors[agency_id].append(
                    WebCollector(agency_id, config.dict())
                )
    
    async def collect_updates(self) -> List[Dict[str, Any]]:
        """Collect updates from all agencies."""
        all_updates = []
        
        for agency_id, collectors in self.collectors.items():
            try:
                agency_updates = []
                
                # Collect updates from each collector for this agency
                for collector in collectors:
                    try:
                        updates = await collector.collect_updates()
                        
                        # Add collector type to updates
                        for update in updates:
                            update["collector_type"] = collector.__class__.__name__
                        
                        agency_updates.extend(updates)
                    except Exception as e:
                        logger.error(
                            f"Error collecting updates from {agency_id} "
                            f"using {collector.__class__.__name__}: {str(e)}"
                        )
                
                # Add agency updates to main list
                all_updates.extend(agency_updates)
                
                # Log collection results
                logger.info(
                    f"Collected {len(agency_updates)} updates from {agency_id}"
                )
                
            except Exception as e:
                logger.error(f"Error processing agency {agency_id}: {str(e)}")
        
        return all_updates
    
    def start_monitoring(self):
        """Start the monitoring scheduler."""
        try:
            # Schedule update collection
            self.scheduler.add_job(
                self.collect_and_process_updates,
                'interval',
                minutes=settings.update_interval_minutes,
                id='regulatory_updates'
            )
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("Regulatory monitoring scheduler started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring scheduler: {str(e)}")
    
    def stop_monitoring(self):
        """Stop the monitoring scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Regulatory monitoring scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping monitoring scheduler: {str(e)}")
    
    async def collect_and_process_updates(self):
        """Collect and process regulatory updates."""
        try:
            # Collect updates
            updates = await self.collect_updates()
            
            if not updates:
                logger.info("No new regulatory updates found")
                return
            
            # Process updates
            await self._process_updates(updates)
            
        except Exception as e:
            logger.error(f"Error in update collection and processing: {str(e)}")
    
    async def _process_updates(self, updates: List[Dict[str, Any]]):
        """Process collected regulatory updates."""
        try:
            # Group updates by agency
            updates_by_agency = {}
            for update in updates:
                agency_id = update["agency_id"]
                if agency_id not in updates_by_agency:
                    updates_by_agency[agency_id] = []
                updates_by_agency[agency_id].append(update)
            
            # Process each agency's updates
            for agency_id, agency_updates in updates_by_agency.items():
                try:
                    # Generate alerts for updates
                    alert_ids = []
                    for update in agency_updates:
                        alert_id = await alert_manager.process_update(update)
                        if alert_id:
                            alert_ids.append(alert_id)
                    
                    if alert_ids:
                        logger.info(
                            f"Generated {len(alert_ids)} alerts for {agency_id}"
                        )
                    
                    # Process alerts
                    await self._process_alerts()
                    
                except Exception as e:
                    logger.error(
                        f"Error processing updates for {agency_id}: {str(e)}"
                    )
            
        except Exception as e:
            logger.error(f"Error processing updates: {str(e)}")
    
    async def _process_alerts(self):
        """Process pending alerts."""
        try:
            # Get pending alerts
            alerts = await alert_manager.get_pending_alerts()
            
            if not alerts:
                return
            
            logger.info(f"Processing {len(alerts)} pending alerts")
            
            for alert in alerts:
                try:
                    # Analyze alert impact
                    analysis = await self._analyze_alert(alert)
                    
                    if analysis:
                        # Update alert with analysis
                        await alert_manager.update_alert_status(
                            alert["id"],
                            "Analyzed",
                            {"analysis": analysis}
                        )
                        
                        # Generate notification if high priority
                        if alert["priority"] == "High":
                            await self._generate_notification(alert)
                            
                            # Update alert status
                            await alert_manager.update_alert_status(
                                alert["id"],
                                "Notified"
                            )
                    
                except Exception as e:
                    logger.error(f"Error processing alert {alert['id']}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error processing alerts: {str(e)}")
    
    async def _analyze_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze alert for impact assessment."""
        # This would be implemented to analyze alert impact
        pass
    
    async def _generate_notification(self, alert: Dict[str, Any]):
        """Generate notification for alert."""
        # This would be implemented to send notifications
        pass

# Singleton instance
regulatory_monitor = RegulatoryMonitor()