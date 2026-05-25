from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    keywords = Column(JSON, default=list)          # ["DG Set", "diesel generator"]
    states = Column(JSON, default=list)            # ["Maharashtra", "Delhi"]
    ministries = Column(JSON, default=list)
    categories = Column(JSON, default=list)
    min_value = Column(Integer, nullable=True)     # INR
    max_value = Column(Integer, nullable=True)     # INR
    sources = Column(JSON, default=list)           # ["gem", "cppp"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="alerts")


class SavedFilter(Base):
    __tablename__ = "saved_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    filters = Column(JSON, default=dict)           # mirrors AlertFilter schema
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_filters")


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    status = Column(String)                        # success / failed / partial
    tenders_found = Column(Integer, default=0)
    tenders_new = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
