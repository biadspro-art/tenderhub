# TenderHub

A full-stack tender scraping and alerting platform. Scrapes government portals (GeM, CPPP, state portals) and sends email alerts when new tenders match your saved filters.

---

## Prerequisites

Install these on your machine before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — runs all services
- That's it. Docker handles Python, Node, PostgreSQL, Redis.

---

## Quick Start

### 1. Clone / extract the project

```bash
cd tenderhub
```

### 2. Configure email (optional for now)

Edit `backend/.env` and fill in your Gmail credentials:

```
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password   # Generate at myaccount.google.com → Security → App Passwords
EMAIL_FROM=your_email@gmail.com
```

You can skip this step and add it later. The app works without email — alerts just won't send.

### 3. Start everything

```bash
docker-compose up --build
```

First run takes 5–10 minutes (downloads images, installs Playwright browsers).

### 4. Open the app

- **Frontend**: http://localhost:3000
- **API docs**: http://localhost:8000/docs

### 5. First-time setup

1. Go to http://localhost:3000 and click **Create one** to register
2. After logging in, go to **Scraper** (admin menu)
3. Click **Scrape Now** next to GeM Portal
4. Watch the scrape log — tenders appear in the Tenders tab once done
5. Go to **Alerts** and create an alert for "DG Set"

---

## How it works

```
Playwright (headless browser)
    ↓  scrapes GeM portal pages
Celery worker (task queue)
    ↓  stores in PostgreSQL
FastAPI backend
    ↓  REST API
React frontend
    ↓  dashboard, filters, alerts
PostgreSQL + Redis
    ↓  data store + task broker
```

**Automatic schedule**: GeM is scraped daily at 7:00 AM and 1:00 PM IST.
**Manual trigger**: Click "Scrape Now" in the Scraper panel (admin only).

---

## Adding a new portal

1. Create `backend/app/scrapers/your_portal_scraper.py` (follow gem_scraper.py as template)
2. Register it in `backend/app/scrapers/__init__.py`
3. Add to the beat schedule in `backend/app/worker.py`

Each scraper just needs to return a list of dicts with these keys:
```python
{
    "source": "your_portal",
    "reference_no": "...",
    "title": "...",
    "department": "...",
    "state": "...",
    "category": "...",
    "tender_value": 1500000.0,        # INR float
    "bid_submission_deadline": datetime,
    "tender_url": "https://...",
    "description": "...",
    "status": "active",
}
```

---

## Project structure

```
tenderhub/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── worker.py            # Celery tasks + schedule
│   │   ├── api/routes/          # auth, tenders, alerts, scraper
│   │   ├── models/              # SQLAlchemy DB models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic
│   │   └── scrapers/            # Scraper modules (one per portal)
│   ├── requirements.txt
│   └── .env                     # Your config (edit this)
└── frontend/
    └── src/
        ├── pages/               # Dashboard, Tenders, Alerts, Scraper, Login
        ├── components/          # Sidebar
        ├── hooks/               # Auth context
        └── utils/api.js         # Axios API client
```

---

## Useful commands

```bash
# View logs from all services
docker-compose logs -f

# View just the scraper worker
docker-compose logs -f worker

# Restart just the backend after code changes
docker-compose restart backend

# Stop everything
docker-compose down

# Stop and delete database (fresh start)
docker-compose down -v
```

---

## Notes on GeM scraping

GeM's public bid listing page (`bidplus.gem.gov.in/all-bids`) is publicly accessible without login. The scraper uses Playwright (a real browser) to navigate the page because GeM uses JavaScript rendering.

- Rate limiting is built in (3-second delays between requests)
- The scraper retries up to 3 times on failure
- If GeM changes its page structure, you'll need to update the CSS selectors in `gem_scraper.py`

---

## Phase 2 roadmap (future additions)

- [ ] CPPP (eprocure.gov.in) scraper
- [ ] Maharashtra, Delhi, Karnataka state portal scrapers
- [ ] Elasticsearch for faster full-text search at scale
- [ ] PDF attachment download and parsing
- [ ] Weekly digest emails
- [ ] Export to Excel/CSV
- [ ] Tender bookmarking per user
- [ ] Admin user management panel
