from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.tender_service import search_tenders
from app.schemas.schemas import TenderListResponse

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("", response_model=TenderListResponse)
def list_tenders(
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None),
    deadline_from: Optional[datetime] = Query(None),
    deadline_to: Optional[datetime] = Query(None),
    status: str = Query("active"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * per_page
    tenders, total = search_tenders(
        db,
        keyword=keyword,
        source=source,
        state=state,
        department=department,
        category=category,
        min_value=min_value,
        max_value=max_value,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        status=status,
        skip=skip,
        limit=per_page,
    )
    return {"tenders": tenders, "total": total, "page": page, "per_page": per_page}
