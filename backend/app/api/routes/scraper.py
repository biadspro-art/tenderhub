from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.models.tender import Tender
from app.models.alert import Alert, ScrapeLog
from app.schemas.schemas import ScrapeRequest, ScrapeLogOut, DashboardStats
from app.scrapers import get_available_sources
from app.worker import scrape_source

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.get("/sources")
def list_sources(current_user: User = Depends(get_current_user)):
    return get_available_sources()


@router.post("/trigger")
def trigger_scrape(
    req: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Manually trigger a scrape (admin only). Runs as a Celery task."""
    task = scrape_source.delay(req.source_id, req.keywords)
    return {"message": f"Scrape triggered for '{req.source_id}'", "task_id": task.id}


@router.get("/logs", response_model=List[ScrapeLogOut])
def scrape_logs(limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(limit).all()


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total_tenders = db.query(Tender).count()
    new_today = db.query(Tender).filter(Tender.scraped_at >= today).count()
    active_alerts = db.query(Alert).filter(Alert.user_id == current_user.id, Alert.is_active == True).count()

    # Tenders by source
    by_source = db.query(Tender.source, func.count(Tender.id)).group_by(Tender.source).all()
    tenders_by_source = {row[0]: row[1] for row in by_source}

    # Tenders by state
    by_state = db.query(Tender.state, func.count(Tender.id)).group_by(Tender.state).limit(10).all()
    tenders_by_state = {row[0] or "Unknown": row[1] for row in by_state}

    recent_scrapes = db.query(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(5).all()

    return DashboardStats(
        total_tenders=total_tenders,
        new_today=new_today,
        active_alerts=active_alerts,
        sources_count=len(tenders_by_source),
        tenders_by_source=tenders_by_source,
        tenders_by_state=tenders_by_state,
        recent_scrapes=recent_scrapes,
    )
