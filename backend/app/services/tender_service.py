import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.tender import Tender
from app.models.alert import Alert, ScrapeLog
from app.models.user import User
from app.services.email_service import send_alert_email

logger = logging.getLogger(__name__)


def upsert_tenders(db: Session, tenders_data: List[dict]) -> tuple[int, int]:
    """Insert new tenders, skip duplicates. Returns (total, new_count)."""
    new_count = 0
    for data in tenders_data:
        existing = db.query(Tender).filter(
            Tender.source == data["source"],
            Tender.reference_no == data["reference_no"],
        ).first()

        if not existing:
            tender = Tender(**data)
            db.add(tender)
            new_count += 1

    db.commit()
    logger.info(f"Upserted {len(tenders_data)} tenders, {new_count} new")
    return len(tenders_data), new_count


def search_tenders(
    db: Session,
    keyword: Optional[str] = None,
    source: Optional[str] = None,
    state: Optional[str] = None,
    department: Optional[str] = None,
    category: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    deadline_from: Optional[datetime] = None,
    deadline_to: Optional[datetime] = None,
    status: str = "active",
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Tender], int]:
    query = db.query(Tender)

    if keyword:
        query = query.filter(
            or_(
                Tender.title.ilike(f"%{keyword}%"),
                Tender.description.ilike(f"%{keyword}%"),
                Tender.department.ilike(f"%{keyword}%"),
            )
        )
    if source:
        query = query.filter(Tender.source == source)
    if state:
        query = query.filter(Tender.state.ilike(f"%{state}%"))
    if department:
        query = query.filter(Tender.department.ilike(f"%{department}%"))
    if category:
        query = query.filter(Tender.category.ilike(f"%{category}%"))
    if min_value is not None:
        query = query.filter(Tender.tender_value >= min_value)
    if max_value is not None:
        query = query.filter(Tender.tender_value <= max_value)
    if deadline_from:
        query = query.filter(Tender.bid_submission_deadline >= deadline_from)
    if deadline_to:
        query = query.filter(Tender.bid_submission_deadline <= deadline_to)
    if status:
        query = query.filter(Tender.status == status)

    total = query.count()
    tenders = query.order_by(Tender.scraped_at.desc()).offset(skip).limit(limit).all()
    return tenders, total


def match_and_notify(db: Session, new_tender_ids: List[int]):
    """Check all active alerts against new tenders and send emails."""
    if not new_tender_ids:
        return

    new_tenders = db.query(Tender).filter(Tender.id.in_(new_tender_ids)).all()
    alerts = db.query(Alert).filter(Alert.is_active == True).all()

    for alert in alerts:
        matched = []
        for tender in new_tenders:
            if _tender_matches_alert(tender, alert):
                matched.append(tender)

        if matched:
            user = db.query(User).filter(User.id == alert.user_id).first()
            if user and user.is_active:
                send_alert_email(user, alert, matched)
                alert.last_triggered_at = datetime.utcnow()

    db.commit()


def _tender_matches_alert(tender: Tender, alert: Alert) -> bool:
    # Keyword match (title or description)
    if alert.keywords:
        text = f"{tender.title} {tender.description or ''}".lower()
        if not any(kw.lower() in text for kw in alert.keywords):
            return False

    # Source filter
    if alert.sources and tender.source not in alert.sources:
        return False

    # State filter
    if alert.states and tender.state not in alert.states:
        return False

    # Ministry filter
    if alert.ministries and tender.ministry not in alert.ministries:
        return False

    # Category filter
    if alert.categories and tender.category not in alert.categories:
        return False

    # Value range
    if alert.min_value and tender.tender_value and tender.tender_value < alert.min_value:
        return False
    if alert.max_value and tender.tender_value and tender.tender_value > alert.max_value:
        return False

    return True


def log_scrape(db: Session, source: str, status: str, found: int, new: int,
               error: str = None, started_at: datetime = None) -> ScrapeLog:
    log = ScrapeLog(
        source=source,
        status=status,
        tenders_found=found,
        tenders_new=new,
        error_message=error,
        started_at=started_at or datetime.utcnow(),
        finished_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log
