#!/usr/bin/env python3
"""
EdTech Certificate Data Collection Framework

This framework provides ethical and respectful collection of publicly available
certificate verification data from major EdTech platforms.

IMPORTANT: This tool is designed for educational and research purposes only.
Always respect platform Terms of Service and rate limits.
"""

import asyncio
import aiohttp
import csv
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CertificateRecord:
    """Data structure for certificate information"""
    learner_name: str = ""
    certificate_title: str = ""
    organization_name: str = ""
    date_issued: str = ""
    certificate_id: str = ""
    verification_url: str = ""
    digital_signature: str = ""
    public_comments: str = ""
    platform: str = ""
    extraction_date: str = ""
    
    def __post_init__(self):
        if not self.extraction_date:
            self.extraction_date = datetime.now().isoformat()

class RateLimiter:
    """Simple rate limiter to respect platform limits"""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
    
    async def wait(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()

class PlatformScraper:
    """Base class for platform-specific scrapers"""
    
    def __init__(self, platform_name: str, rate_limit: float = 1.0):
        self.platform_name = platform_name
        self.rate_limiter = RateLimiter(rate_limit)
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content with rate limiting"""
        await self.rate_limiter.wait()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_certificate_data(self, html_content: str, url: str) -> Optional[CertificateRecord]:
        """Override in subclasses to extract platform-specific data"""
        raise NotImplementedError("Subclasses must implement extract_certificate_data")

class CourseraVerificationScraper(PlatformScraper):
    """Scraper for Coursera certificate verification pages"""
    
    def __init__(self):
        super().__init__("Coursera", rate_limit=0.5)  # Conservative rate limit
    
    def extract_certificate_data(self, html_content: str, url: str) -> Optional[CertificateRecord]:
        """Extract data from Coursera verification pages"""
        if not html_content or "accomplishments/verify" not in url:
            return None
        
        record = CertificateRecord(platform="Coursera", verification_url=url)
        
        try:
            # Extract learner name
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
            if name_match:
                record.learner_name = name_match.group(1).strip()
            
            # Extract certificate title
            title_match = re.search(r'<h2[^>]*>([^<]+)</h2>', html_content)
            if title_match:
                record.certificate_title = title_match.group(1).strip()
            
            # Extract organization (Coursera partner)
            org_match = re.search(r'by ([^<]+)', html_content)
            if org_match:
                record.organization_name = org_match.group(1).strip()
            
            # Extract completion date
            date_match = re.search(r'completed on ([^<]+)', html_content)
            if date_match:
                record.date_issued = date_match.group(1).strip()
            
            # Extract certificate ID from URL
            id_match = re.search(r'/verify/([A-Z0-9]+)', url)
            if id_match:
                record.certificate_id = id_match.group(1)
            
            return record if record.learner_name else None
            
        except Exception as e:
            logger.error(f"Error extracting Coursera data from {url}: {e}")
            return None

class NPTELVerificationScraper(PlatformScraper):
    """Scraper for NPTEL certificate verification"""
    
    def __init__(self):
        super().__init__("NPTEL", rate_limit=0.3)  # Very conservative for government site
    
    def extract_certificate_data(self, html_content: str, url: str) -> Optional[CertificateRecord]:
        """Extract data from NPTEL verification pages"""
        if not html_content:
            return None
        
        record = CertificateRecord(platform="NPTEL", verification_url=url)
        
        try:
            # NPTEL specific extraction patterns
            # Note: Actual implementation would depend on NPTEL's public verification format
            
            # Extract student name
            name_match = re.search(r'Student Name[:\s]*([^<\n]+)', html_content, re.IGNORECASE)
            if name_match:
                record.learner_name = name_match.group(1).strip()
            
            # Extract course title
            course_match = re.search(r'Course[:\s]*([^<\n]+)', html_content, re.IGNORECASE)
            if course_match:
                record.certificate_title = course_match.group(1).strip()
            
            # NPTEL is the organization
            record.organization_name = "NPTEL"
            
            # Extract certificate number
            cert_match = re.search(r'Certificate[:\s]*([A-Z0-9]+)', html_content, re.IGNORECASE)
            if cert_match:
                record.certificate_id = cert_match.group(1).strip()
            
            return record if record.learner_name else None
            
        except Exception as e:
            logger.error(f"Error extracting NPTEL data from {url}: {e}")
            return None

class LinkedInLearningVerificationScraper(PlatformScraper):
    """Scraper for LinkedIn Learning certificate verification"""
    
    def __init__(self):
        super().__init__("LinkedIn Learning", rate_limit=0.3)
    
    def extract_certificate_data(self, html_content: str, url: str) -> Optional[CertificateRecord]:
        """Extract data from LinkedIn Learning certificate share pages"""
        if not html_content:
            return None
        
        record = CertificateRecord(platform="LinkedIn Learning", verification_url=url)
        
        try:
            # LinkedIn specific extraction patterns
            # Note: LinkedIn certificate pages have specific structures
            
            # Extract learner name
            name_match = re.search(r'"name"[:\s]*"([^"]+)"', html_content)
            if name_match:
                record.learner_name = name_match.group(1).strip()
            
            # Extract course title
            title_match = re.search(r'"courseName"[:\s]*"([^"]+)"', html_content)
            if title_match:
                record.certificate_title = title_match.group(1).strip()
            
            # LinkedIn Learning is the organization
            record.organization_name = "LinkedIn Learning"
            
            # Extract completion date
            date_match = re.search(r'"completionDate"[:\s]*"([^"]+)"', html_content)
            if date_match:
                record.date_issued = date_match.group(1).strip()
            
            return record if record.learner_name else None
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn data from {url}: {e}")
            return None

class DigitalBadgeVerifier(PlatformScraper):
    """Scraper for digital badge verification (Credly, etc.)"""
    
    def __init__(self):
        super().__init__("Digital Badges", rate_limit=0.5)
    
    def extract_certificate_data(self, html_content: str, url: str) -> Optional[CertificateRecord]:
        """Extract data from digital badge verification pages"""
        if not html_content:
            return None
        
        record = CertificateRecord(platform="Digital Badge", verification_url=url)
        
        try:
            # Extract badge holder name
            name_match = re.search(r'badge-holder[^>]*>([^<]+)', html_content, re.IGNORECASE)
            if name_match:
                record.learner_name = name_match.group(1).strip()
            
            # Extract badge title
            title_match = re.search(r'badge-title[^>]*>([^<]+)', html_content, re.IGNORECASE)
            if title_match:
                record.certificate_title = title_match.group(1).strip()
            
            # Extract issuer
            issuer_match = re.search(r'issuer[^>]*>([^<]+)', html_content, re.IGNORECASE)
            if issuer_match:
                record.organization_name = issuer_match.group(1).strip()
            
            # Extract issue date
            date_match = re.search(r'issued[^>]*>([^<]+)', html_content, re.IGNORECASE)
            if date_match:
                record.date_issued = date_match.group(1).strip()
            
            return record if record.learner_name else None
            
        except Exception as e:
            logger.error(f"Error extracting badge data from {url}: {e}")
            return None

class CertificateDataCollector:
    """Main coordinator for certificate data collection"""
    
    def __init__(self):
        self.scrapers = {
            'coursera': CourseraVerificationScraper(),
            'nptel': NPTELVerificationScraper(),
            'linkedin': LinkedInLearningVerificationScraper(),
            'badges': DigitalBadgeVerifier()
        }
        self.collected_data: List[CertificateRecord] = []
    
    async def collect_from_urls(self, urls: List[str]) -> List[CertificateRecord]:
        """Collect certificate data from a list of verification URLs"""
        results = []
        
        for url in urls:
            try:
                # Determine appropriate scraper based on URL
                scraper = self._get_scraper_for_url(url)
                if not scraper:
                    logger.warning(f"No appropriate scraper for URL: {url}")
                    continue
                
                async with scraper:
                    html_content = await scraper.fetch_url(url)
                    if html_content:
                        record = scraper.extract_certificate_data(html_content, url)
                        if record:
                            results.append(record)
                            logger.info(f"Successfully extracted data from {url}")
                        else:
                            logger.warning(f"No data extracted from {url}")
                    else:
                        logger.warning(f"Failed to fetch content from {url}")
                
                # Add delay between different URLs
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
        
        self.collected_data.extend(results)
        return results
    
    def _get_scraper_for_url(self, url: str) -> Optional[PlatformScraper]:
        """Determine which scraper to use based on URL"""
        url_lower = url.lower()
        
        if 'coursera.org' in url_lower and 'verify' in url_lower:
            return self.scrapers['coursera']
        elif 'nptel' in url_lower:
            return self.scrapers['nptel']
        elif 'linkedin.com' in url_lower and ('learning' in url_lower or 'certificate' in url_lower):
            return self.scrapers['linkedin']
        elif any(domain in url_lower for domain in ['credly.com', 'badgr.com', 'blockcerts']):
            return self.scrapers['badges']
        
        return None
    
    def export_to_json(self, filename: str = "certificate_data.json"):
        """Export collected data to JSON format"""
        data = [asdict(record) for record in self.collected_data]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(data)} records to {filename}")
    
    def export_to_csv(self, filename: str = "certificate_data.csv"):
        """Export collected data to CSV format"""
        if not self.collected_data:
            logger.warning("No data to export")
            return
        
        fieldnames = [
            'learner_name', 'certificate_title', 'organization_name',
            'date_issued', 'certificate_id', 'verification_url',
            'digital_signature', 'public_comments', 'platform',
            'extraction_date'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in self.collected_data:
                writer.writerow(asdict(record))
        
        logger.info(f"Exported {len(self.collected_data)} records to {filename}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected data"""
        if not self.collected_data:
            return {"total_records": 0}
        
        platform_counts = {}
        organization_counts = {}
        
        for record in self.collected_data:
            platform_counts[record.platform] = platform_counts.get(record.platform, 0) + 1
            if record.organization_name:
                organization_counts[record.organization_name] = organization_counts.get(record.organization_name, 0) + 1
        
        return {
            "total_records": len(self.collected_data),
            "platforms": platform_counts,
            "organizations": organization_counts,
            "date_range": {
                "earliest": min(r.extraction_date for r in self.collected_data if r.extraction_date),
                "latest": max(r.extraction_date for r in self.collected_data if r.extraction_date)
            }
        }

async def main():
    """Example usage of the certificate data collector"""
    
    # Example verification URLs (these should be real, publicly accessible URLs)
    sample_urls = [
        # Coursera verification URLs (examples)
        "https://www.coursera.org/account/accomplishments/verify/SAMPLE123",
        
        # LinkedIn Learning certificate share URLs (examples)
        "https://www.linkedin.com/learning/certificates/sample",
        
        # Add more sample URLs here for testing
    ]
    
    collector = CertificateDataCollector()
    
    logger.info("Starting certificate data collection...")
    results = await collector.collect_from_urls(sample_urls)
    
    if results:
        logger.info(f"Collected {len(results)} certificate records")
        
        # Export data
        collector.export_to_json("certificates.json")
        collector.export_to_csv("certificates.csv")
        
        # Print statistics
        stats = collector.get_statistics()
        logger.info(f"Collection statistics: {json.dumps(stats, indent=2)}")
    else:
        logger.warning("No certificate data was collected")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())