from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail


def send_inquiry_notification(inquiry) -> None:
    """Notify the business owner when a new inquiry comes in."""
    recipient = current_app.config.get("ADMIN_NOTIFICATION_EMAIL")
    if not recipient:
        current_app.logger.warning("ADMIN_NOTIFICATION_EMAIL not set - skipping email notification")
        return

    offering_name = inquiry.offering.name if inquiry.offering else "General inquiry"
    msg = Message(
        subject=f"New inquiry from {inquiry.name}",
        recipients=[recipient],
        body=(
            f"New inquiry received.\n\n"
            f"Name: {inquiry.name}\n"
            f"Email: {inquiry.email}\n"
            f"Phone: {inquiry.phone or 'N/A'}\n"
            f"Regarding: {offering_name}\n\n"
            f"Message:\n{inquiry.message}\n"
        ),
    )
    mail.send(msg)


def send_password_reset_email(admin, reset_url: str) -> None:
    msg = Message(
        subject="Reset your admin password",
        recipients=[admin.email],
        body=(
            f"Hi {admin.username},\n\n"
            f"Click the link below to reset your password. This link expires in 1 hour.\n\n"
            f"{reset_url}\n\n"
            f"If you didn't request this, you can safely ignore this email."
        ),
    )
    mail.send(msg)
