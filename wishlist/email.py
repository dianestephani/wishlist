import logging

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_email(subject, html_body):
    """Send an email via Resend API. Fails silently if not configured."""
    if not settings.RESEND_API_KEY or not settings.NOTIFICATION_TO_EMAIL:
        logger.warning("Resend not configured — skipping email: %s", subject)
        return None

    resend.api_key = settings.RESEND_API_KEY

    try:
        return resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [settings.NOTIFICATION_TO_EMAIL],
                "subject": subject,
                "html": html_body,
            }
        )
    except Exception:
        logger.exception("Failed to send email: %s", subject)
        return None


def send_purchased_email(user, item, message=""):
    subject = f"{item.title} has been purchased!"

    body = (
        f"<p>{user.first_name} {user.last_name} purchased <strong>{item.title}</strong> "
        f"for you! They can be reached at {user.email}"
    )
    if user.phone_number:
        body += f" and {user.phone_number}"
    body += ".</p>"

    if message:
        body += f'<p><strong>Their message:</strong> "{message}"</p>'

    return _send_email(subject, body)


def send_undo_email(user, item, message=""):
    subject = f"Just kidding! {item.title} was NOT purchased."

    body = (
        f"<p>{user.first_name} {user.last_name} lied to you about buying "
        f"<strong>{item.title}</strong> for your birthday! Make them regret their "
        f"mistake by reaching them at {user.email}"
    )
    if user.phone_number:
        body += f" or {user.phone_number}"
    body += ".</p>"

    if message:
        body += f'<p><strong>Their message:</strong> "{message}"</p>'

    return _send_email(subject, body)
