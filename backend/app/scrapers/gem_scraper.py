"""
GeM (Government e-Marketplace) tender scraper.
Uses GeM's public API - no browser needed.
"""

import logging
import re
from datetime import datetime
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

GEM_API_URL = "https://bidplus.gem.gov.in/all-bids"
GEM_API_SEARCH = "https://bidplus.gem.gov.in/bidlists"
GEM_BASE_URL = "https://bidplus.gem.gov.in"

DG_SET_KEYWORDS = ["DG Set", "diesel generator", "generating set", "genset"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://bidplus.gem.gov.in/all-bids",
}


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = ["%d/%m/%Y %I:%M %p", "%d-%m-%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def parse_value(value_str: Optional[str]) -> Optional[float]:
    if not value_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", str(value_str).replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return None


class GeMScraper:
    def __init__(self, keywords: list = None, max_pages: int = 5):
        self.keywords = keywords or DG_SET_KEYWORDS
        self.max_pages = max_pages

    async def scrape(self) -> list:
        all_tenders = []
        async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            for keyword in self.keywords:
                logger.info(f"[GeM] Scraping keyword: {keyword}")
                tenders = await self._scrape_keyword(client, keyword)
                all_tenders.extend(tenders)
                logger.info(f"[GeM] Found {len(tenders)} tenders for '{keyword}'")

        # Deduplicate by bid number
        seen = set()
        unique = []
        for t in all_tenders:
            key = t.get("reference_no")
            if key and key not in seen:
                seen.add(key)
                unique.append(t)

        logger.info(f"[GeM] Total unique tenders: {len(unique)}")
        return unique

    async def _scrape_keyword(self, client: httpx.AsyncClient, keyword: str) -> list:
        tenders = []
        for page_num in range(1, self.max_pages + 1):
            try:
                # GeM API endpoint for bid search
                params = {
                    "searchedBid": keyword,
                    "page": page_num,
                }
                response = await client.get(GEM_API_SEARCH, params=params)
                logger.info(f"[GeM] API response status: {response.status_code} for keyword '{keyword}' page {page_num}")

                if response.status_code != 200:
                    logger.warning(f"[GeM] Non-200 response: {response.status_code}")
                    break

                # Try JSON first
                try:
                    data = response.json()
                    page_tenders = self._parse_json_response(data, keyword)
                except Exception:
                    # Fall back to parsing HTML text
                    page_tenders = self._parse_text_response(response.text, keyword)

                if not page_tenders:
                    logger.info(f"[GeM] No more results for '{keyword}' at page {page_num}")
                    break

                tenders.extend(page_tenders)

            except httpx.RequestError as e:
                logger.error(f"[GeM] Request error for keyword '{keyword}': {e}")
                break
            except Exception as e:
                logger.error(f"[GeM] Error on page {page_num} for '{keyword}': {e}")
                break

        return tenders

    def _parse_json_response(self, data: dict, keyword: str) -> list:
        tenders = []
        # Handle different possible JSON structures from GeM
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("data", data.get("bids", data.get("results", [])))

        for item in items:
            if not isinstance(item, dict):
                continue
            tender = {
                "source": "gem",
                "reference_no": item.get("bid_number") or item.get("bidNumber") or item.get("reference_no") or f"GEM-{hash(str(item)) % 1000000:06d}",
                "title": item.get("bid_title") or item.get("title") or item.get("name") or keyword,
                "department": item.get("department") or item.get("dept_name") or "Government of India",
                "ministry": item.get("ministry") or None,
                "state": item.get("state") or "Central",
                "category": item.get("category") or keyword,
                "tender_value": parse_value(item.get("estimated_value") or item.get("tender_value")),
                "bid_submission_deadline": parse_date(item.get("end_date") or item.get("closing_date") or item.get("bid_end_date")),
                "opening_date": None,
                "tender_url": item.get("url") or f"{GEM_BASE_URL}/bidlists",
                "description": str(item)[:500],
                "status": "active",
            }
            tenders.append(tender)
        return tenders

    def _parse_text_response(self, text: str, keyword: str) -> list:
        tenders = []
        # Extract bid numbers from HTML/text response
        bid_numbers = re.findall(r"GEM/\d+/[A-Z]/\d+", text)
        for bid_no in bid_numbers:
            tenders.append({
                "source": "gem",
                "reference_no": bid_no,
                "title": f"{keyword} - {bid_no}",
                "department": "Government of India",
                "ministry": None,
                "state": "Central",
                "category": keyword,
                "tender_value": None,
                "bid_submission_deadline": None,
                "opening_date": None,
                "tender_url": f"{GEM_BASE_URL}/bidlists?searchedBid={keyword}",
                "description": f"GeM tender {bid_no} matching keyword: {keyword}",
                "status": "active",
            })
        return tenders


async def run_gem_scraper(keywords: list = None, max_pages: int = 5) -> list:
    scraper = GeMScraper(keywords=keywords, max_pages=max_pages)
    return await scraper.scrape()
