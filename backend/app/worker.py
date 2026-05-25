import asyncio
import logging
from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

celery_app = Celery(
    "tenderhub",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Scheduled tasks
    beat_schedule={
        "scrape-gem-daily": {
            "task": "app.worker.scrape_source",
            "schedule": crontab(hour=7, minute=0),       # Every day at 7 AM IST
            "args": ["gem"],
        },
        "scrape-gem-midday": {
            "task": "app.worker.scrape_source",
            "schedule": crontab(hour=13, minute=0),      # Every day at 1 PM IST
            "args": ["gem"],
        },
    },
)


@celery_app.task(bind=True, name="app.worker.scrape_source", max_retries=3)
def scrape_source(self, source_id: str, keywords: list = None):
    """Celery task: run a scraper for a given source and store results."""
    from app.scrapers import run_scraper
    from app.services.tender_service import upsert_tenders, match_and_notify, log_scrape

    db = SessionLocal()
    started_at = datetime.utcnow()
    logger.info(f"[Worker] Starting scrape for source: {source_id}")

    try:
        # Run the async scraper inside the sync Celery task
        tenders_data = asyncio.run(run_scraper(source_id, keywords=keywords))
        total, new_count = upsert_tenders(db, tenders_data)

        # Get IDs of newly inserted tenders for alert matching
        from app.models.tender import Tender
        recent = db.query(Tender.id).filter(
            Tender.source == source_id
        ).order_by(Tender.created_at.desc()).limit(new_count).all()
        new_ids = [r.id for r in recent]

        if new_ids:
            match_and_notify(db, new_ids)

        log_scrape(db, source_id, "success", total, new_count, started_at=started_at)
        logger.info(f"[Worker] Done scraping {source_id}: {total} found, {new_count} new")
        return {"source": source_id, "total": total, "new": new_count}

    except Exception as exc:
        logger.error(f"[Worker] Scrape failed for {source_id}: {exc}")
        log_scrape(db, source_id, "failed", 0, 0, error=str(exc), started_at=started_at)
        raise self.retry(exc=exc, countdown=60)

    finally:
        db.close()
