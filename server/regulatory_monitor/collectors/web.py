import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import re
import ssl

from .base import UpdateCollector

logger = logging.getLogger(__name__)

class WebCollector(UpdateCollector):
    """Collector for web scraping based updates."""
    
    async def collect_updates(self) -> List[Dict[str, Any]]:
        """Collect updates by scraping web pages."""
        updates = []
        
        # Create SSL context that accepts self-signed certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connection with custom SSL context
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=conn) as session:
            for url in self.config.get("web_scraping_urls", []):
                try:
                    # Fetch page content with SSL verification disabled
                    async with session.get(url, ssl=False) as response:
                        if response.status == 200:
                            html = await response.text()
                            
                            # Parse updates based on agency-specific selectors
                            page_updates = await self._parse_page(url, html)
                            updates.extend(page_updates)
                        else:
                            logger.error(
                                f"Failed to fetch {url}: Status {response.status}"
                            )
                
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
                    continue
        
        return updates
    
    async def _parse_page(self, url: str, html: str) -> List[Dict[str, Any]]:
        """Parse page content based on agency-specific selectors."""
        updates = []
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            if self.agency_id == "OCC":
                updates.extend(self._parse_occ_page(soup, url))
            elif self.agency_id == "FinCEN":
                updates.extend(self._parse_fincen_page(soup, url))
            elif self.agency_id == "FHFA":
                updates.extend(self._parse_fhfa_page(soup, url))
            # Add more agency-specific parsers as needed
            
        except Exception as e:
            logger.error(
                f"Error parsing page for {self.agency_id} from {url}: {str(e)}"
            )
        
        return updates
    
    def _parse_occ_page(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse OCC bulletins and updates."""
        updates = []
        
        # Find bulletin entries
        for entry in soup.find_all("div", class_="bulletin-entry"):
            try:
                # Extract title
                title_elem = entry.find("h3")
                if not title_elem:
                    continue
                title = self._clean_text(title_elem.get_text())
                
                # Extract date
                date_elem = entry.find("span", class_="date")
                if not date_elem:
                    continue
                date_text = self._clean_text(date_elem.get_text())
                published_date = self._parse_date(date_text)
                
                # Extract content
                content_elem = entry.find("div", class_="content")
                content = self._clean_text(content_elem.get_text()) if content_elem else ""
                
                # Extract bulletin number
                bulletin_number = ""
                bulletin_match = re.search(r"Bulletin\s+(\d{4}-\d+)", title)
                if bulletin_match:
                    bulletin_number = bulletin_match.group(1)
                
                # Create update
                update = self.format_update(
                    title=title,
                    content=content,
                    update_type="Bulletin",
                    published_date=published_date,
                    url=self._extract_link(entry, url),
                    metadata={
                        "bulletin_number": bulletin_number,
                        "categories": self._extract_categories(entry)
                    }
                )
                
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error parsing OCC bulletin entry: {str(e)}")
                continue
        
        return updates
    
    def _parse_fincen_page(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse FinCEN news and updates."""
        updates = []
        
        # Find news entries
        for entry in soup.find_all("div", class_="news-item"):
            try:
                # Extract title
                title_elem = entry.find("h2")
                if not title_elem:
                    continue
                title = self._clean_text(title_elem.get_text())
                
                # Extract date
                date_elem = entry.find("span", class_="date")
                if not date_elem:
                    continue
                date_text = self._clean_text(date_elem.get_text())
                published_date = self._parse_date(date_text)
                
                # Extract content
                content_elem = entry.find("div", class_="summary")
                content = self._clean_text(content_elem.get_text()) if content_elem else ""
                
                # Determine update type
                update_type = self._determine_fincen_update_type(title, content)
                
                # Create update
                update = self.format_update(
                    title=title,
                    content=content,
                    update_type=update_type,
                    published_date=published_date,
                    url=self._extract_link(entry, url),
                    metadata={
                        "topics": self._extract_topics(entry)
                    }
                )
                
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error parsing FinCEN news entry: {str(e)}")
                continue
        
        return updates
    
    def _parse_fhfa_page(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse FHFA news and updates."""
        updates = []
        
        # Find news entries
        for entry in soup.find_all("article", class_="news-release"):
            try:
                # Extract title
                title_elem = entry.find("h3")
                if not title_elem:
                    continue
                title = self._clean_text(title_elem.get_text())
                
                # Extract date
                date_elem = entry.find("time")
                if not date_elem:
                    continue
                date_text = self._clean_text(date_elem.get_text())
                published_date = self._parse_date(date_text)
                
                # Extract content
                content_elem = entry.find("div", class_="content")
                content = self._clean_text(content_elem.get_text()) if content_elem else ""
                
                # Create update
                update = self.format_update(
                    title=title,
                    content=content,
                    update_type="News Release",
                    published_date=published_date,
                    url=self._extract_link(entry, url),
                    metadata={
                        "release_number": self._extract_release_number(entry),
                        "categories": self._extract_categories(entry)
                    }
                )
                
                updates.append(update)
                
            except Exception as e:
                logger.error(f"Error parsing FHFA news entry: {str(e)}")
                continue
        
        return updates
    
    def _extract_link(self, element: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract and normalize link from element."""
        link_elem = element.find("a")
        if not link_elem or not link_elem.get("href"):
            return None
        
        href = link_elem["href"]
        if href.startswith("http"):
            return href
        elif href.startswith("//"):
            return f"https:{href}"
        elif href.startswith("/"):
            return f"{base_url.rstrip('/')}{href}"
        else:
            return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
    
    def _extract_categories(self, element: BeautifulSoup) -> List[str]:
        """Extract categories from element."""
        categories = []
        category_elements = element.find_all("span", class_="category")
        
        for cat_elem in category_elements:
            category = self._clean_text(cat_elem.get_text())
            if category:
                categories.append(category)
        
        return categories
    
    def _extract_topics(self, element: BeautifulSoup) -> List[str]:
        """Extract topics from element."""
        topics = []
        topic_elements = element.find_all("span", class_="topic")
        
        for topic_elem in topic_elements:
            topic = self._clean_text(topic_elem.get_text())
            if topic:
                topics.append(topic)
        
        return topics
    
    def _extract_release_number(self, element: BeautifulSoup) -> Optional[str]:
        """Extract release number from element."""
        release_elem = element.find("span", class_="release-number")
        if release_elem:
            return self._clean_text(release_elem.get_text())
        return None
    
    def _determine_fincen_update_type(self, title: str, content: str) -> str:
        """Determine FinCEN update type based on content."""
        title_lower = title.lower()
        content_lower = content.lower()
        
        if "advisory" in title_lower or "advisory" in content_lower:
            return "Advisory"
        elif "guidance" in title_lower or "guidance" in content_lower:
            return "Guidance"
        elif "notice" in title_lower or "notice" in content_lower:
            return "Notice"
        elif "enforcement" in title_lower or "enforcement" in content_lower:
            return "Enforcement Action"
        else:
            return "News Release"
    
    def _parse_date(self, date_text: str) -> datetime:
        """Parse date from text in various formats."""
        date_formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_text}")