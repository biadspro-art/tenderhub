import logging
import httpx
import os

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FRONTEND_URL = "https://humorous-peace-production-3cd3.up.railway.app"


def send_alert_email(user, alert, tenders):
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set - skipping email")
        return False

    count = len(tenders)
    rows = ""
    for t in tenders:
        deadline = t.bid_submission_deadline.strftime("%d %b %Y") if t.bid_submission_deadline else "N/A"
        value = "Rs.{:,.0f}".format(t.tender_value) if t.tender_value else "N/A"
        rows += "<tr><td style='padding:8px'><a href='{}'>{}</a><br><small>{}</small></td><td style='padding:8px'>{}</td><td style='padding:8px'>{}</td><td style='padding:8px'>{}</td></tr>".format(
            t.tender_url or "#", t.title, t.reference_no, t.department or "N/A", value, deadline
        )

    html = "<html><body><h2>TenderHub Alert: {}</h2><p>Hi {},</p><p>Found {} new tender(s) matching your alert.</p><table border='1' cellpadding='8'><tr><th>Tender</th><th>Department</th><th>Value</th><th>Deadline</th></tr>{}</table><p><a href='{}/tenders'>View on TenderHub</a></p></body></html>".format(
        alert.name, user.full_name, count, rows, FRONTEND_URL
    )

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": "Bearer " + RESEND_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "from": "TenderHub <onboarding@resend.dev>",
"to": ["biadspro@gmail.com"],
                "subject": "[TenderHub] {} new tender(s) for: {}".format(count, alert.name),
                "html": html,
            },
            timeout=10,
        )
        if response.status_code in (200, 201):
            logger.info("Email sent to {}".format(user.email))
            return True
        else:
            logger.error("Resend error: {} - {}".format(response.status_code, response.text))
            return False
    except Exception as e:
        logger.error("Email failed: {}".format(e))
        return False
