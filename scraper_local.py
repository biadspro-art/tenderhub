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
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://bidplus.gem.gov.in/all-bids",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        for page in range(1, 4):
            url = "https://bidplus.gem.gov.in/all-bids"
            params = {
                "searchedBid": keyword,
                "page_no": page,
            }
            response = httpx.get(url, params=params, headers=headers, timeout=30, follow_redirects=True)
            print(f"[GeM] keyword='{keyword}' page={page} status={response.status_code} size={len(response.text)}")

            if response.status_code != 200:
                print(f"[GeM] Error response: {response.text[:200]}")
                break

            import re
            bid_numbers = re.findall(r"GEM/\d+/[A-Z]/\d+", response.text)
            print(f"[GeM] Found bid numbers: {bid_numbers[:5]}")

            if not bid_numbers:
                break

            for bid_no in set(bid_numbers):
                tenders.append({
                    "source": "gem",
                    "reference_no": bid_no,
                    "title": "{} - {}".format(keyword, bid_no),
                    "department": "Government of India",
                    "state": "Central",
                    "category": keyword,
                    "tender_url": "https://bidplus.gem.gov.in/bidlists?searchedBid={}".format(keyword),
                    "status": "active",
                })

    except Exception as e:
        print(f"[GeM] Error: {e}")
    return tenders


def scrape_cppp(keyword):
    """Scrape Central Public Procurement Portal"""
    tenders = []
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        url = "https://eprocure.gov.in/eprocure/app"
        params = {
            "page": "FrontEndTendersByKeyword",
            "service": "page",
            "kw": keyword,
        }
        response = httpx.get(url, params=params, headers=headers, timeout=30, follow_redirects=True)
        print(f"[CPPP] keyword='{keyword}' status={response.status_code} size={len(response.text)}")
        print(f"[CPPP] Response preview: {response.text[:500]}")

        import re
        # Try multiple patterns
        patterns = [
            r"\d{4}_[A-Z]+_\d+_\d+",
            r"NIT\s*No[:\s]+([^\s<]+)",
            r"Tender\s*ID[:\s]+([^\s<]+)",
            r"tender_id=(\d+)",
            r"TenderId=(\d+)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                print(f"[CPPP] Pattern '{pattern}' found: {matches[:5]}")
                for ref in set(matches):
                    tenders.append({
                        "source": "cppp",
                        "reference_no": str(ref),
                        "title": "{} - {}".format(keyword, ref),
                        "department": "Government of India",
                        "state": "Central",
                        "category": keyword,
                        "tender_url": "https://eprocure.gov.in/eprocure/app?page=FrontEndTendersByKeyword&service=page&kw={}".format(keyword),
                        "status": "active",
                    })
                break

    except Exception as e:
        print(f"[CPPP] Error: {e}")
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
    print("Saved {} new tenders out of {} found".format(new_count, len(tenders)))
    return new_count


if __name__ == "__main__":
    all_tenders = []
    for keyword in KEYWORDS:
        # Skip GeM for now - blocks cloud IPs
        cppp_tenders = scrape_cppp(keyword)
        all_tenders.extend(cppp_tenders)
        print("Found {} CPPP tenders for '{}'".format(len(cppp_tenders), keyword))

    seen = set()
    unique = []
    for t in all_tenders:
        key = "{}-{}".format(t["source"], t["reference_no"])
        if key not in seen:
            seen.add(key)
            unique.append(t)

    print("Total unique tenders: {}".format(len(unique)))
    save_tenders(unique)
