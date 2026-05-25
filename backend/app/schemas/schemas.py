from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Tender ---
class TenderOut(BaseModel):
    id: int
    source: str
    reference_no: str
    title: str
    department: Optional[str]
    ministry: Optional[str]
    state: Optional[str]
    category: Optional[str]
    tender_value: Optional[float]
    bid_submission_deadline: Optional[datetime]
    opening_date: Optional[datetime]
    tender_url: Optional[str]
    status: str
    scraped_at: datetime

    class Config:
        from_attributes = True


class TenderListResponse(BaseModel):
    tenders: List[TenderOut]
    total: int
    page: int
    per_page: int


# --- Alert ---
class AlertCreate(BaseModel):
    name: str
    keywords: List[str] = []
    states: List[str] = []
    ministries: List[str] = []
    categories: List[str] = []
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    sources: List[str] = ["gem"]


class AlertOut(BaseModel):
    id: int
    name: str
    keywords: List[str]
    states: List[str]
    ministries: List[str]
    categories: List[str]
    min_value: Optional[int]
    max_value: Optional[int]
    sources: List[str]
    is_active: bool
    created_at: datetime
    last_triggered_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Saved Filter ---
class SavedFilterCreate(BaseModel):
    name: str
    filters: dict


class SavedFilterOut(BaseModel):
    id: int
    name: str
    filters: dict
    created_at: datetime

    class Config:
        from_attributes = True


# --- Scrape ---
class ScrapeRequest(BaseModel):
    source_id: str
    keywords: Optional[List[str]] = None


class ScrapeLogOut(BaseModel):
    id: int
    source: str
    status: str
    tenders_found: int
    tenders_new: int
    error_message: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Dashboard ---
class DashboardStats(BaseModel):
    total_tenders: int
    new_today: int
    active_alerts: int
    sources_count: int
    tenders_by_source: dict
    tenders_by_state: dict
    recent_scrapes: List[ScrapeLogOut]
