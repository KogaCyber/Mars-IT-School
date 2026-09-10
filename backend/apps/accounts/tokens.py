"""Refresh tokenlarni bekor qilish (revocation) mantiqi."""

import logging
import random

# `datetime.UTC` — Python 3.11 dan boshlab. `timezone.utc` esa aynan o'sha
# obyekt va u barcha qo'llab-quvvatlanadigan versiyalarda bor
# (paketlar minimumi — 3.10). Aks holda ilova 3.10 da import paytidayoq
# qulardi va bu faqat serverda ma'lum bo'lardi.
from datetime import datetime
from datetime import timezone as dt_timezone

from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RevokedRefreshToken

logger = logging.getLogger(__name__)

#: Bekor qilishlarning taxminan shuncha ulushida eskilari tozalanadi.
#: Muddati o'tgan yozuv hech narsani himoya qilmaydi — token allaqachon
#: yaroqsiz. Ular yig'ilib qolsa kolleksiya cheksiz o'sardi va `purge_revoked_tokens`
#: buyrug'ini cron'ga qo'yish esa esdan chiqadigan qo'lda ish edi.
_CLEANUP_PROBABILITY = 0.02


def purge_expired() -> int:
    """Muddati o'tgan yozuvlarni o'chiradi va nechtasini o'chirganini qaytaradi."""
    deleted, _ = RevokedRefreshToken.objects.filter(expires_at__lt=timezone.now()).delete()
    return deleted


def _maybe_purge_expired() -> None:
    """Vaqti-vaqti bilan eski yozuvlarni tozalaydi (xatolik asosiy amalni buzmaydi)."""
    if random.random() >= _CLEANUP_PROBABILITY:  # noqa: S311 — kriptografiya emas
        return
    try:
        purge_expired()
    except Exception:  # noqa: BLE001 — tozalash chiqishni buzmasligi kerak
        logger.exception("Muddati o'tgan tokenlarni tozalab bo'lmadi")


def revoke(token: RefreshToken) -> None:
    """Refresh tokenni bekor qilinganlar ro'yxatiga qo'shadi (takroran chaqirish xavfsiz)."""
    jti = token.payload.get("jti")
    if not jti:
        return

    expires_at = datetime.fromtimestamp(token.payload.get("exp", 0), tz=dt_timezone.utc)
    RevokedRefreshToken.objects.get_or_create(
        jti=jti,
        defaults={"user_id": token.payload.get("user_id"), "expires_at": expires_at},
    )
    _maybe_purge_expired()


def is_revoked(token: RefreshToken) -> bool:
    jti = token.payload.get("jti")
    return bool(jti) and RevokedRefreshToken.objects.filter(jti=jti).exists()


def ensure_active(token: RefreshToken) -> None:
    """Token bekor qilingan bo'lsa xatolik ko'taradi."""
    if is_revoked(token):
        raise TokenError("Token bekor qilingan.")
