from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from datetime import datetime
from app.db.database import Base


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)               # e.g. "gem", "cppp", "maharashtra"
    reference_no = Column(String, index=True)
    title = Column(Text, nullable=False)
    department = Column(String, index=True)
    ministry = Column(String)
    state = Column(String, index=True)
    category = Column(String, index=True)             # e.g. "DG Set", "IT", "Construction"
    tender_value = Column(Float)                       # in INR
    bid_submission_deadline = Column(DateTime)
    opening_date = Column(DateTime)
    tender_url = Column(Text)
    description = Column(Text)
    status = Column(String, default="active")          # active / closed / cancelled
    scraped_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source", "reference_no", name="uq_source_ref"),
    )
