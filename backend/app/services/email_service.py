import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.core.config import settings
from app.models.alert import Alert
from app.models.tender import Tender
from app.models.user import User

logger = logging.getLogger(__name__)


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

    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:700px;margin:auto;padding:20px">
      <div style="background:#1a56db;color:white;padding:20px;border-radius:8px 8px 0 0">
        <h2 style="margin:0">🔔 TenderHub Alert: {alert.name}</h2>
        <p style="margin:4px 0 0;opacity:.8">{len(tenders)} new tender(s) matching your alert</p>
      </div>
      <div style="border:1px solid #eee;border-top:none;padding:20px;border-radius:0 0 8px 8px">
        <p>Hi {user.full_name},</p>
        <p>We found <strong>{len(tenders)} new tender(s)</strong> matching your alert <strong>"{alert.name}"</strong>.</p>
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
          <a href="http://localhost:3000/tenders" style="background:#1a56db;color:white;padding:10px 20px;text-decoration:none;border-radius:6px">
            View All on TenderHub →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0">
        <p style="color:#888;font-size:12px">
          You're receiving this because you set up an alert on TenderHub.
          <a href="http://localhost:3000/alerts">Manage your alerts</a>
        </p>
      </div>
    </body></html>
    """


def send_alert_email(user: User, alert: Alert, tenders: List[Tender]) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[TenderHub] {len(tenders)} new tender(s) for: {alert.name}"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = user.email

        html_body = build_alert_email(user, alert, tenders)
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, user.email, msg.as_string())

        logger.info(f"Alert email sent to {user.email} for alert '{alert.name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to send alert email to {user.email}: {e}")
        return False
