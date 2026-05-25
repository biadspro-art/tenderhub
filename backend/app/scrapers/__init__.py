"""
Central registry for all scrapers.
To add a new source: implement the same interface as GeMScraper
and register it here.
"""

from app.scrapers.gem_scraper import run_gem_scraper

SCRAPER_REGISTRY = {
    "gem": {
        "name": "GeM Portal",
        "url": "https://bidplus.gem.gov.in",
        "runner": run_gem_scraper,
        "description": "Government e-Marketplace - Central government procurement",
    },
    # Future scrapers - plug in when ready:
    # "cppp": {
    #     "name": "CPPP",
    #     "url": "https://eprocure.gov.in",
    #     "runner": run_cppp_scraper,
    #     "description": "Central Public Procurement Portal",
    # },
    # "maharashtra": {
    #     "name": "Maharashtra Tenders",
    #     "url": "https://mahatenders.gov.in",
    #     "runner": run_maharashtra_scraper,
    #     "description": "Maharashtra state tenders",
    # },
}


def get_available_sources():
    return [
        {"id": k, "name": v["name"], "url": v["url"], "description": v["description"]}
        for k, v in SCRAPER_REGISTRY.items()
    ]


async def run_scraper(source_id: str, **kwargs) -> list[dict]:
    if source_id not in SCRAPER_REGISTRY:
        raise ValueError(f"Unknown source: {source_id}")
    runner = SCRAPER_REGISTRY[source_id]["runner"]
    return await runner(**kwargs)
