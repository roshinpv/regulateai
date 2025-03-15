import feedparser
from datetime import datetime
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup

from .base import UpdateCollector

logger = logging.getLogger(__name__)

class RSSCollector(UpdateCollector):
    """Collector for RSS feed updates."""
    
    async def collect_updates(self) -> List[Dict[str, Any]]:
        """Collect updates from RSS feeds."""
        updates = []
        
        for feed_url in self.config.get("rss_feeds", []):
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    try:
                        # Parse date
                        published_date = datetime(*entry.published_parsed[:6])
                        
                        # Clean content
                        content = entry.get("description", "")
                        if content:
                            # Remove HTML tags while preserving text
                            soup = BeautifulSoup(content, "html.parser")
                            content = soup.get_text()
                            content = self._clean_text(content)
                        
                        # Determine update type
                        update_type = self._determine_update_type(entry.title, content)
                        
                        # Format update
                        update = self.format_update(
                            title=entry.title,
                            content=content,
                            update_type=update_type,
                            published_date=published_date,
                            url=entry.link,
                            metadata={
                                "feed_url": feed_url,
                                "guid": entry.get("id", ""),
                                "author": entry.get("author", ""),
                                "categories": entry.get("tags", [])
                            }
                        )
                        
                        updates.append(update)
                        
                    except Exception as e:
                        logger.error(f"Error processing RSS entry from {feed_url}: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
                continue
        
        return updates
    
    def _determine_update_type(self, title: str, content: str) -> str:
        """Determine the type of regulatory update based on content."""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Check for enforcement actions
        if any(term in title_lower or term in content_lower 
               for term in ["enforcement", "violation", "penalty", "fine"]):
            return "Enforcement Action"
        
        # Check for guidance
        if any(term in title_lower or term in content_lower 
               for term in ["guidance", "advisory", "bulletin"]):
            return "Guidance"
        
        # Check for rule changes
        if any(term in title_lower or term in content_lower 
               for term in ["rule", "regulation", "requirement"]):
            return "Rule Change"
        
        # Default to general update
        return "General Update"