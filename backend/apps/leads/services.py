"""Ariza kelganda xabar yuborish xizmatlari."""

import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _format_message(lead) -> str:
    lines = [
        "Yangi ariza — Mars IT School",
        f"Ism: {lead.full_name}",
        f"Telefon: {lead.phone}",
        f"Kurs: {lead.course.title_ru if lead.course else '—'}",
        f"Manba: {lead.get_source_display()}",
    ]
    if lead.comment:
        lines.append(f"Izoh: {lead.comment}")
    return "\n".join(lines)


def notify_new_lead(lead) -> None:
    """Email va Telegram orqali xabar yuboradi. Xatolik arizani buzmasligi kerak."""
    message = _format_message(lead)

    if settings.LEAD_NOTIFY_EMAILS:
        try:
            send_mail(
                subject=f"Yangi ariza: {lead.full_name}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.LEAD_NOTIFY_EMAILS,
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Ariza haqida email yuborilmadi (lead_id=%s)", lead.pk)

    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if token and chat_id:
        try:
            payload = urllib.parse.urlencode(
                {"chat_id": chat_id, "text": message}
            ).encode()
            request = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage", data=payload
            )
            # Manzil doimiy (api.telegram.org) — foydalanuvchi kiritmaydi.
            with urllib.request.urlopen(request, timeout=5):  # noqa: S310
                pass
        except Exception:  # noqa: BLE001
            logger.exception("Ariza haqida Telegram xabari yuborilmadi (lead_id=%s)", lead.pk)
