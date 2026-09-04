"""Ariza kelganda xabar yuborish xizmatlari.

Xabar yuborish HECH QACHON so'rov oqimida bajarilmaydi. Sabab ikkita:

* **Tezlik.** SMTP (10 s timeout) va Telegram (5 s) tashqi xizmatlar. Gunicorn
  `--threads 8` bilan ishlaydi — sekin SMTP host bir necha daqiqada barcha
  oqimlarni band qilib, saytni butunlay to'xtatib qo'yishi mumkin edi. Bu
  hujumchi uchun juda arzon DoS: bir necha o'nlab ariza yuborilsa yetarli.
* **Foydalanuvchi.** Ariza yuborgan odam tashqi xizmatning javobini kutishi
  kerak emas — uning arizasi allaqachon bazaga yozilgan.

Shuning uchun yuborish alohida oqimga (`daemon` thread) chiqariladi.
"""

import logging
import threading
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

#: Bir vaqtda shuncha xabar oqimi ishlashi mumkin. Cheklov bo'lmasa, ko'p
#: sonli ariza (yoki botlar hujumi) cheksiz oqim yaratib, jarayonning
#: xotirasini tugatib qo'yardi. Limitga yetilganda xabar shunchaki
#: yuborilmaydi — ariza esa baribir bazada saqlangan.
_MAX_WORKERS = 8
_slots = threading.BoundedSemaphore(_MAX_WORKERS)


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


def _safe_subject(name: str) -> str:
    """Email sarlavhasi uchun xavfsiz matn.

    `full_name` foydalanuvchidan keladi. Unda `\r` yoki `\n` bo'lsa — bu
    email sarlavhasiga o'z qatorlarini (masalan `Bcc:`) qo'shish urinishi
    bo'lardi. Django buni `BadHeaderError` bilan to'xtatadi, lekin biz
    umuman bunday holatga yetkazmaymiz.
    """
    cleaned = " ".join(str(name or "").split())
    return f"Yangi ariza: {cleaned[:80]}"


def notify_new_lead(lead) -> None:
    """Xabar yuborishni fon oqimida boshlaydi (so'rovni bloklamaydi)."""
    message = _format_message(lead)
    subject = _safe_subject(lead.full_name)
    lead_id = lead.pk

    if not _slots.acquire(blocking=False):
        logger.warning(
            "Xabar oqimlari limiti to'ldi — ariza bildirishnomasi o'tkazib "
            "yuborildi (lead_id=%s). Ariza bazada saqlangan.",
            lead_id,
        )
        return

    def run() -> None:
        try:
            _send(subject, message, lead_id)
        finally:
            _slots.release()

    threading.Thread(target=run, name=f"lead-notify-{lead_id}", daemon=True).start()


def _send(subject: str, message: str, lead_id) -> None:
    """Email va Telegram orqali xabar yuboradi. Xatolik arizani buzmasligi kerak."""

    if settings.LEAD_NOTIFY_EMAILS:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.LEAD_NOTIFY_EMAILS,
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Ariza haqida email yuborilmadi (lead_id=%s)", lead_id)

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
            logger.exception("Ariza haqida Telegram xabari yuborilmadi (lead_id=%s)", lead_id)
