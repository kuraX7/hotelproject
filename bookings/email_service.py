"""
Email service for hotel bookings.
All email logic is centralized here — easy to maintain and extend.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from content.models import HotelInfo
import logging

logger = logging.getLogger(__name__)


def _get_hotel_info():
    return HotelInfo.objects.first()


def _build_context(booking, extra=None):
    """Base context shared across all email templates."""
    ctx = {
        'booking': booking,
        'info': _get_hotel_info(),
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'dashboard_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
    }
    if extra:
        ctx.update(extra)
    return ctx


def _send_email(subject, to_email, template_html, context, reply_to=None):
    """
    Generic email sender.
    Returns True on success, False on failure.
    Never raises — errors are logged.
    """
    try:
        html_content = render_to_string(template_html, context)
        # Plain text fallback (simple strip of HTML)
        import re
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            reply_to=[reply_to] if reply_to else None,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email FAILED to {to_email}: {e}")
        return False


# ── PUBLIC FUNCTIONS ──────────────────────────────────

def send_booking_confirmation_to_client(booking):
    """
    Email sent to the CLIENT after a successful booking.
    Subject: "Confirmation de votre réservation #AL00001 — Al Andalus"
    """
    info = _get_hotel_info()
    hotel_name = info.hotel_name if info else "Al Andalus"
    subject = f"✅ Confirmation de réservation #AL{booking.id:05d} — {hotel_name}"
    context = _build_context(booking)
    return _send_email(
        subject=subject,
        to_email=booking.email,
        template_html='emails/booking_confirmation_client.html',
        context=context,
        reply_to=info.email if info else None,
    )


def send_booking_notification_to_admin(booking):
    """
    Email sent to the ADMIN when a new booking is created.
    Subject: "🔔 Nouvelle réservation #AL00001 — Nom du client"
    """
    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    if not admin_email:
        logger.warning("ADMIN_EMAIL not set — admin notification skipped.")
        return False
    subject = f"🔔 Nouvelle réservation #AL{booking.id:05d} — {booking.name}"
    context = _build_context(booking)
    return _send_email(
        subject=subject,
        to_email=admin_email,
        template_html='emails/booking_notification_admin.html',
        context=context,
    )


def send_booking_cancellation_to_client(booking):
    """
    Email sent to the CLIENT when their booking is cancelled.
    Subject: "Annulation de votre réservation #AL00001"
    """
    info = _get_hotel_info()
    hotel_name = info.hotel_name if info else "Al Andalus"
    subject = f"Annulation de votre réservation #AL{booking.id:05d} — {hotel_name}"
    context = _build_context(booking)
    return _send_email(
        subject=subject,
        to_email=booking.email,
        template_html='emails/booking_cancellation_client.html',
        context=context,
    )


def send_booking_status_update_to_client(booking):
    """
    Email sent when admin changes booking status.
    Dispatches to the right template based on new status.
    """
    if booking.status == 'confirmed':
        return send_booking_confirmation_to_client(booking)
    elif booking.status == 'cancelled':
        return send_booking_cancellation_to_client(booking)
    return False
