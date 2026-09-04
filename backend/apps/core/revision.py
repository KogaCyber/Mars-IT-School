"""Kontent versiyasi — saytdagi jonli (real vaqtdagi) yangilanish uchun.

Sayt statik emas: admin panelda kontent o'zgarganda ochiq turgan sahifa buni
o'zi bilib olishi kerak. Buning uchun bitta kichik raqam — «revision» —
saqlanadi va har qanday o'zgarishda (`signals.py`) yangilanadi:

  * frontend uni qisqa oraliqda so'rab turadi va o'zgarganda kontentni qayta
    yuklaydi (SSE/WebSocket o'rniga: gunicorn `gthread` bilan ishlaydi va
    ochiq ulanishlar soni cheklangan — uzoq ulanishlar worker'ni band qilardi);
  * ochiq API javoblari keshining kalitiga qo'shiladi — versiya o'zgarishi
    bilan eski javob avtomatik yaroqsiz bo'ladi (`cache.py`).

Raqam MongoDB'da saqlanadi, chunki u barcha worker'lar uchun umumiy bo'lishi
kerak (mahalliy kesh har bir jarayonda alohida). Har so'rovda bazaga
murojaat qilmaslik uchun qiymat `LOCAL_TTL` soniyaga keshlanadi — ya'ni
o'zgarish eng ko'pi bilan shuncha soniyadan keyin barcha worker'larga yetadi.
"""

import logging
import time

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = "content:revision"
#: Bazadagi qiymat shuncha soniya mahalliy keshda ushlanadi.
LOCAL_TTL = 2


def read_revision() -> int:
    """Bazadagi haqiqiy qiymat (keshsiz)."""
    from .models import SiteRevision

    row = SiteRevision.objects.values_list("value", flat=True).first()
    return int(row or 0)


def current_revision() -> int:
    """Qisqa muddat keshlangan qiymat — har so'rovda baza o'qilmaydi."""
    value = cache.get(CACHE_KEY)
    if value is None:
        try:
            value = read_revision()
        except Exception:  # noqa: BLE001 — versiya o'qilmasa ham sayt ishlashi kerak
            logger.exception("Kontent versiyasini o'qib bo'lmadi")
            return 0
        cache.set(CACHE_KEY, value, LOCAL_TTL)
    return value


def bump_revision() -> int:
    """Versiyani yangi vaqt tamg'asiga ko'taradi."""
    from .models import SiteRevision

    value = int(time.time() * 1000)
    if not SiteRevision.objects.update(value=value):
        SiteRevision.objects.create(value=value)
    cache.set(CACHE_KEY, value, LOCAL_TTL)
    return value
