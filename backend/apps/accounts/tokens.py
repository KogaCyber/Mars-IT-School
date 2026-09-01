"""Refresh tokenlarni bekor qilish (revocation) mantiqi."""

from datetime import UTC, datetime

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RevokedRefreshToken


def revoke(token: RefreshToken) -> None:
    """Refresh tokenni bekor qilinganlar ro'yxatiga qo'shadi (takroran chaqirish xavfsiz)."""
    jti = token.payload.get("jti")
    if not jti:
        return

    expires_at = datetime.fromtimestamp(token.payload.get("exp", 0), tz=UTC)
    RevokedRefreshToken.objects.get_or_create(
        jti=jti,
        defaults={"user_id": token.payload.get("user_id"), "expires_at": expires_at},
    )


def is_revoked(token: RefreshToken) -> bool:
    jti = token.payload.get("jti")
    return bool(jti) and RevokedRefreshToken.objects.filter(jti=jti).exists()


def ensure_active(token: RefreshToken) -> None:
    """Token bekor qilingan bo'lsa xatolik ko'taradi."""
    if is_revoked(token):
        raise TokenError("Token bekor qilingan.")
