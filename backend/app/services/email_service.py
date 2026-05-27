import logging
import httpx
from typing import List
from app.core.config import settings
from app.models.alert import Alert
from app.models.tender import Tender
from app.models.user import User
import os

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")


def build_alert_email(user: User, alert: Alert, tenders: List[Tender]) -> str:
    rows = ""
    for t in tenders:
        deadline = t.bid_submission_deadline.strftime("%d %b %Y") if t.bid_submission_deadline else "N/A"
        value = f"₹{t.tender_value:,.0f}" if t.tender_value else "N/A"
        url = t.tender_url or "#"
        rows += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #eee">
            <a href="{url}" style="color:#1a56db;text-decoration:none;font-weight:500">{t.title}</a>
            <br><small style="color:#888">{t.reference_no} · {t.source.upper()}</small>
          </td>
          <td style="padding:10px;border-bottom:1px solid #eee;color:#555">{t.department or 'N/A'}</td>
          <td style="padding:10px;border-bottom:1px solid #eee;color:#555">{value}</td>
          <td style="padding:10px;border-bottom:1px solid #eee;color:#e53e3e;font-weight:500">{deadline}</td>
        </tr>
        """

    frontend_url = "https://humorous-peace-production-3cd3.up.railway.app"

    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:700px;margin:auto;padding:20px">
      <div style="background:#1a56db;color:white;padding:20px;border-radius:8px 8px 0 0">
        <h2 style="margin:0">🔔 TenderHub Alert: {alert.name}</h2>
        <p style="margin:4px 0 0;opacity:.8">{len(tenders)} new tender(s) matching your alert</p>
      </div>
      <div style="border:1px solid #eee;border-top:none;padding:20px;border-radius:0 0 8px 8px">
        <p>Hi {user.full_name},</p>
        <p>We found <strong>{len(tend
