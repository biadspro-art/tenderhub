import os
import httpx
import psycopg2
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")
KEYWORDS = ["DG Set", "diesel generator", "generating set", "genset"]

def get_db():
    return psycopg2.connect(DATABASE_URL)

def scrape_gem(keyword):
    tenders = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        for page in range(1, 6):
            response = httpx.get(
                "https://bidplus.gem.gov.in/bidlists",
                params={"searchedBid": keyword, "page": page},
                headers=headers,
                timeout=30,
                follow_redirects=True,
            )
            print(f"[GeM] keyword='{keyword}' page={page} status={response.status_code}")
            if response.status_code != 200:
                break

            import re
            bid_numbers = re.findall(r"GEM/\d+/[A-Z]/\d+", response.text)
            if not bid_numbers:
                break

            for bid_no in bid_numbers:
                tenders.append({
                    "source": "gem",
                    "reference_no": bid_no,
                    "title": f"{keyword} - {bid_no}",
                    "department": "Government of India",
                    "state": "Central",
                    "category": keyword,
                    "tender_url": f"https://bidplus.gem.gov.in/bidlists?searchedBid={keyword}",
                    "status": "active",
                })
    except Exception as e:
        print(f"[GeM] Error: {e}")
    return tenders

def save_tenders(tenders):
    if not tenders:
        print("No tenders to save")
        return 0

    conn = get_db()
    cur = conn.cursor()
    new_count = 0

    for t in tenders:
        cur.execute(
            "SELECT id FROM tenders WHERE source=%s AND reference_no=%s",
            (t["source"], t["reference_no"])
        )
        if cur.fetchone():
            continue

        cur.execute("""
            INSERT INTO tenders (source, reference_no, title, department, state, category, tender_url, status, scraped_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            t["source"], t["reference_no"], t["title"],
            t["department"], t["state"], t["category"],
            t["tender_url"], t["status"], datetime.utcnow()
        ))
        new_count += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Saved {new_count} new tenders out of {len(tenders)} found")
    return new_count

if __name__ == "__main__":
    all_tenders = []
    for keyword in KEYWORDS:
        tenders = scrape_gem(keyword)
        all_tenders.extend(tenders)
        print(f"Found {len(tenders)} for '{keyword}'")

    seen = set()
    unique = []
    for t in all_tenders:
        if t["reference_no"] not in seen:
            seen.add(t["reference_no"])
            unique.append(t)

    save_tenders(unique)
