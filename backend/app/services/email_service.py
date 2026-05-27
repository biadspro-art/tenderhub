import logging
import httpx
from typing import List
from app.models.alert import Alert
from app.models.tender import Tender
from app.models.user import User
import os

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FRONTEND_URL = "https://humorous-peace-production-3cd3.up.railway.app"


def build_alert_email(user, alert, tenders):
    rows = ""
    for t in tenders:
        deadline = t.bid_submission_deadline.strftime("%d %b %Y") if t.bid_submission_deadline else "N/A"
        value = "Rs.{:,.0f}".format(t.tender_value) if t.tender_value else "N/A"
        url = t.tender_url or "#"
        rows += "<tr>"
        rows += "<td style='padding:10px;border-bottom:1px solid #eee'>"
        rows += "<a href='{}' style='color:#1a56db'>{}</a>".format(url, t.title)
        rows += "<br><small>{} - {}</small>".format(t.reference_no, t.source.upper())
        rows += "</td>"
        rows += "<td style='padding:10px;border-bottom:1px solid #eee'>{}</td>".format(t.department or "N/A")
        rows += "<td style='padding:10px;border-bottom:1px solid #eee'>{}</td>".format(value)
        rows += "<td style='padding:10px;border-bottom:1px solid #eee;color:#e53e3e'>{}</td>".format(deadline)
        rows += "</tr>"

    count = len(tenders)
    name = alert.name
    full_name = user.full_name

    html = """
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:700px;margin:auto;padding:20px">
  <div style="background:#1a56db;color:white;padding:20px;border-radius:8px 8px 0 0">
    <h2 style="margin:0">TenderHub Alert: {name}</h2>
    <p style="margin:4px 0 0;opacity:.8">{count} new tender(s) matching your alert</p>
  </div>
  <div style="border:1px solid #eee;border-top:none;padding:20px;border-radius:0 0 8px 8px">
    <p>Hi {full_name},</p>
    <p>We found <b>{count} new tender(s)</b> matching your alert <b>{name}</b>.</p>
    <table width="100%" style="border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="background:#f7f8fa">
          <th style="padding:10px;text-align:left">Tender</th>
          <th style="padding:10px;text-align:left">Department</th>
          <th style="padding:10px;text-align:left">Value</th>
          <th style="padding:10px;text-align:left">Deadline</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="margin-top:20px">
      <a href="{frontend}/tenders" style="background:#1a56db;color:white;padding:10px 20px;text-decoration:none;border-radius:6px">
        View All on TenderHub
      </a>
    </p>
  </div>
</body></html>
""".format(name=name, count=count, full_name=full_name, rows=rows, frontend=FRONTEND_URL)

    return html


def send_alert_email(user, alert, tenders):
    if not RESEND_API_KEY:
