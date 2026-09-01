"""Foydalanuvchi ma'lumotlari uchun validatorlar."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# O'zbekiston raqami: +998 XX XXX XX XX
UZ_PHONE_RE = re.compile(r"^\+998\d{9}$")


def validate_uz_phone(value: str) -> None:
    if not UZ_PHONE_RE.match(value or ""):
        raise ValidationError(
            _("Telefon raqam +998XXXXXXXXX ko'rinishida bo'lishi kerak."),
            code="invalid_phone",
        )


def normalize_phone(value: str) -> str:
    """Foydalanuvchi kiritgan raqamni +998XXXXXXXXX ko'rinishiga keltiradi."""
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("998"):
        digits = digits[3:]
    digits = digits[-9:]
    return f"+998{digits}" if digits else ""
