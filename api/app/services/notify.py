"""Ariza kelganda xabar: email va Telegram. Hech qachon so'rovni bloklamaydi.

Yuborish fon vazifasida (FastAPI `BackgroundTasks`), xatolik arizani
buzmaydi — u allaqachon bazada. Bir vaqtda ko'pi bilan `_MAX_WORKERS` ta
yuborish: botlar hujumi cheksiz vazifa yaratib xotirani tugatmasin.
"""

import asyncio
import logging
import smtplib
import urllib.parse
import urllib.request
from email.message import EmailMessage

from ..config import get_settings

logger = logging.getLogger(__name__)
_slots = asyncio.Semaphore(8)


def _safe_subject(name: str) -> str:
    # `\r\n` — email sarlavhasiga o'z qatorini qo'shish urinishi bo'lardi.
    return f"Yangi ariza: {' '.join(str(name or '').split())[:80]}"


def _send_email(subject: str, body: str) -> None:
    s = get_settings()
    if not (s.lead_notify_emails and s.smtp_host):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = s.default_from_email
    msg["To"] = ", ".join(s.lead_notify_emails)
    msg.set_content(body)
    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=10) as smtp:
        smtp.starttls()
        if s.smtp_user:
            smtp.login(s.smtp_user, s.smtp_password)
        smtp.send_message(msg)


def _send_telegram(body: str) -> None:
    s = get_settings()
    if not (s.telegram_bot_token and s.telegram_chat_id):
        return
    payload = urllib.parse.urlencode({"chat_id": s.telegram_chat_id, "text": body}).encode()
    req = urllib.request.Request(  # noqa: S310 — manzil doimiy, foydalanuvchi kiritmaydi
        f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage", data=payload
    )
    with urllib.request.urlopen(req, timeout=5):  # noqa: S310
        pass


async def notify_new_lead(full_name: str, phone: str, course: str, source: str, comment: str) -> None:
    lines = [
        "Yangi ariza — Mars IT School",
        f"Ism: {full_name}",
        f"Telefon: {phone}",
        f"Kurs: {course or '—'}",
        f"Manba: {source}",
    ]
    if comment:
        lines.append(f"Izoh: {comment}")
    body = "\n".join(lines)
    subject = _safe_subject(full_name)

    if _slots.locked():
        logger.warning("Xabar oqimlari band — bildirishnoma o'tkazib yuborildi (%s)", phone)
        return
    async with _slots:
        for fn, args in ((_send_email, (subject, body)), (_send_telegram, (body,))):
            try:
                await asyncio.to_thread(fn, *args)
            except Exception:  # noqa: BLE001
                logger.exception("Ariza bildirishnomasi yuborilmadi (%s)", fn.__name__)
