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
                    # Save updates to database
                    await self._save_updates(agency_updates)
                    
                    # Analyze updates for impact
                    await self._analyze_updates(agency_updates)
                    
                    # Generate notifications
                    await self._generate_notifications(agency_updates)
                    
                except Exception as e:
                    logger.error(
                        f"Error processing updates for {agency_id}: {str(e)}"
                    )
            
        except Exception as e:
            logger.error(f"Error processing updates: {str(e)}")
    
    async def _save_updates(self, updates: List[Dict[str, Any]]):
        """Save regulatory updates to database."""
        # This would be implemented to save to your database
        pass
    
    async def _analyze_updates(self, updates: List[Dict[str, Any]]):
        """Analyze updates for regulatory impact."""
        # This would be implemented to analyze updates
        pass
    
    async def _generate_notifications(self, updates: List[Dict[str, Any]]):
        """Generate notifications for relevant updates."""
        # This would be implemented to generate notifications
        pass

# Singleton instance
regulatory_monitor = RegulatoryMonitor()