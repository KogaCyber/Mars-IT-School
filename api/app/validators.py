"""Kiruvchi ma'lumotlarni tekshirish — telefon, honeypot."""

import re

from pydantic import field_validator

UZ_PHONE_RE = re.compile(r"^\+998\d{9}$")


def normalize_phone(value: str) -> str:
    """`90 123 45 67`, `+998 (90) 123-45-67`, `998901234567` → `+998901234567`."""
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("998"):
        digits = digits[3:]
    digits = digits[-9:]
    return f"+998{digits}" if digits else ""


def validate_uz_phone(value: str) -> str:
    phone = normalize_phone(value)
    if not UZ_PHONE_RE.match(phone):
        raise ValueError("Telefon raqam +998XXXXXXXXX ko'rinishida bo'lishi kerak.")
    return phone


def phone_field(optional: bool = False):
    """Pydantic validator: raqamni normallashtiradi va tekshiradi."""

    def _validate(cls, value):  # noqa: ANN001
        if optional and not value:
            return ""
        return validate_uz_phone(value)

    return field_validator("phone", mode="before")(classmethod(_validate))
