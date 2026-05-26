"""
GeM (Government e-Marketplace) tender scraper.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

GEM_BASE_URL = "https://bidplus.gem.gov.in"
GEM_BIDS_URL = f"{GEM_BASE_URL}/all-bids"

DG_SET_KEYWORDS = ["DG Set", "diesel generator", "generating set", "genset", "DG"]


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = ["%d/%m/%Y %I:%M %p", "%d-%m-%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def parse_value(value_str: Optional[str]) -> Optional[float]:
    if not value_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", value_str.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return None


class GeMScraper:
    def __init__(self, keywords: list = None, max_pages: int = 10):
        self.keywords = keywords or DG_SET_KEYWORDS
        self.max_pages = max_pages

    async def scrape(self) -> list:
        all_tenders = []
        try:
            async with async_playwright() as p:
                logger.info("[GeM] Launching browser...")
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--single-process",
                        "--no-zygote",
                    ]
                )
                logger.info("[GeM] Browser launched successfully")
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = await context.new_page()

                for keyword in self.keywords:
                    logger.info(f"[GeM] Scraping keyword: {keyword}")
                    tenders = await self._scrape_keyword(page, keyword)
                    all_tenders.extend(tenders)
                    await asyncio.sleep(3)

                await browser.close()
        except Exception as e:
            logger.error(f"[GeM] BROWSER ERROR: {type(e).__name__}: {e}", exc_info=True)
            raise

        seen = set()
        unique = []
        for t in all_tenders:
            key = t.get("reference_no")
            if key and key not in seen:
                seen.add(key)
                unique.append(t)

        logger.info(f"[GeM] Total unique tenders found: {len(unique)}")
        return unique

    async def _scrape_keyword(self, page, keyword: str) -> list:
        tenders = []
        try:
            await page.goto(GEM_BIDS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            search_selectors = [
                "input[placeholder*='Search']",
                "input[placeholder*='search']",
                "input[name='search']",
                "#search",
                ".search-input",
            ]
            for sel in search_selectors:
                try:
                    await page.fill(sel, keyword, timeout=5000)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(3000)
                    break
                except Exception:
                    continue

            for page_num in range(1, self.max_pages + 1):
                logger.info(f"[GeM] Scraping page {page_num} for '{keyword}'")
                page_tenders = await self._extract_tenders_from_page(page, keyword)
                tenders.extend(page_tenders)

                if not page_tenders:
                    break

                next_clicked = await self._go_next_page(page)
                if not next_clicked:
                    break
                await page.wait_for_timeout(2000)

        except PlaywrightTimeout:
            logger.warning(f"[GeM] Timeout scraping keyword: {keyword}")
        except Exception as e:
            logger.error(f"[GeM] Error scraping keyword '{keyword}': {e}")

        return tenders

    async def _extract_tenders_from_page(self, page, keyword: str) -> list:
        tenders = []
        try:
            card_selectors = [
                ".bid-list-card", ".bid-card", ".tender-card",
                "[class*='bid-item']", ".card.bid",
            ]
            cards = []
            for sel in card_selectors:
                cards = await page.query_selector_all(sel)
                if cards:
                    break

            if not cards:
                cards = await page.query_selector_all("table tbody tr")

            logger.info(f"[GeM] Found {len(cards)} items on page")

            for card in cards:
                try:
                    tender = await self._parse_card(card, keyword)
                    if tender:
                        tenders.append(tender)
                except Exception as e:
                    logger.debug(f"[GeM] Error parsing card: {e}")

        except Exception as e:
            logger.error(f"[GeM] Error extracting from page: {e}")

        return tenders

    async def _parse_card(self, card, keyword: str) -> Optional[dict]:
        text = await card.inner_text()
        if not text.strip():
            return None

        bid_no_match = re.search(r"GEM/\d+/[A-Z]/\d+", text)
        bid_no = bid_no_match.group(0) if bid_no_match else None

        link = await card.query_selector("a[href*='bid']")
        url = None

async def run_gem_scraper(keywords: list = None, max_pages: int = 5) -> list:
    scraper = GeMScraper(keywords=keywords, max_pages=max_pages)
    return await scraper.scrape()
