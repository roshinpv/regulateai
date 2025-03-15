from pydantic_settings import BaseSettings
from typing import Dict, Any, List
import os

class AgencyConfig(BaseSettings):
    name: str
    update_types: List[str]
    access_methods: List[str]
    rss_feeds: List[str] = []
    api_endpoints: Dict[str, str] = {}
    web_scraping_urls: List[str] = []
    api_key: Optional[str] = None

class MonitoringConfig(BaseSettings):
    agencies: Dict[str, AgencyConfig] = {
        "OCC": AgencyConfig(
            name="Office of the Comptroller of the Currency",
            update_types=["Bulletins", "Enforcement Actions"],
            access_methods=["RSS", "Web Scraping"],
            rss_feeds=["https://www.occ.gov/news-issuances/news-releases/rss.xml"],
            web_scraping_urls=["https://www.occ.gov/news-issuances/bulletins/"]
        ),
        "CFPB": AgencyConfig(
            name="Consumer Financial Protection Bureau",
            update_types=["Consumer Financial Laws", "Compliance Guidelines"],
            access_methods=["API"],
            api_endpoints={
                "regulations": "https://api.consumerfinance.gov/regulations/",
                "enforcement": "https://api.consumerfinance.gov/enforcement/"
            },
            api_key=os.getenv("CFPB_API_KEY")
        ),
        "FDIC": AgencyConfig(
            name="Federal Deposit Insurance Corporation",
            update_types=["Banking Regulations", "Compliance Updates"],
            access_methods=["RSS"],
            rss_feeds=[
                "https://www.fdic.gov/rss/press-releases.rss",
                "https://www.fdic.gov/rss/regulations.rss"
            ]
        ),
        "FinCEN": AgencyConfig(
            name="Financial Crimes Enforcement Network",
            update_types=["AML", "KYC", "SARs"],
            access_methods=["Web Scraping", "RSS"],
            rss_feeds=["https://www.fincen.gov/news/news.xml"],
            web_scraping_urls=["https://www.fincen.gov/news-room"]
        ),
        "FederalReserve": AgencyConfig(
            name="Federal Reserve",
            update_types=["Monetary Policy", "Stress Testing", "Risk Management"],
            access_methods=["API"],
            api_endpoints={
                "press_releases": "https://api.federalreserve.gov/press/",
                "supervision": "https://api.federalreserve.gov/supervision/"
            },
            api_key=os.getenv("FED_API_KEY")
        ),
        "SEC": AgencyConfig(
            name="Securities and Exchange Commission",
            update_types=["Securities Regulations", "Compliance Actions"],
            access_methods=["API"],
            api_endpoints={
                "edgar": "https://data.sec.gov/submissions/",
                "rules": "https://www.sec.gov/rules/final.rss"
            },
            api_key=os.getenv("SEC_API_KEY")
        )
    }
    
    update_interval_minutes: int = int(os.getenv("UPDATE_INTERVAL_MINUTES", "60"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay_seconds: int = int(os.getenv("RETRY_DELAY_SECONDS", "60"))
    
    class Config:
        env_file = ".env"

settings = MonitoringConfig()