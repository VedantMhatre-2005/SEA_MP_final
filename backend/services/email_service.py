"""Email service for OTP delivery."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from config.settings import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)

logger = logging.getLogger(__name__)


def send_otp_email(recipient_email: str, otp: str, purpose: str) -> None:
    """Send OTP email. Falls back to logging OTP if SMTP is not configured."""
    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP not configured. OTP for %s (%s): %s", recipient_email, purpose, otp)
        return

    subject = f"ASPRAMS {purpose.title()} OTP"
    body = (
        f"Your OTP for ASPRAMS {purpose} is: {otp}\n\n"
        "This OTP expires in 10 minutes.\n"
        "If you did not request this, you can ignore this email."
    )

    message = EmailMessage()
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning(
            "Failed to send OTP email to %s for %s. Falling back to log output: %s",
            recipient_email,
            purpose,
            exc,
        )
        logger.warning("OTP for %s (%s): %s", recipient_email, purpose, otp)
