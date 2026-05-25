import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import create_tables
from app.api.routes import auth, tenders, alerts, scraper

app = FastAPI(
    title="TenderHub API",
    version="1.0.0",
    description="Tender scraping and alerting platform",
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tightened after you get your Railway URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}


app.include_router(auth.router, prefix="/api")
app.include_router(tenders.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(scraper.router, prefix="/api")
