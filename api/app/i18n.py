"""Uch til: ru / uz / en. Tarjima maydonlari `title_ru`, `title_uz`, `title_en`.

Bo'sh tarjima o'rniga asosiy til (ru) qiymati beriladi — eski Django backend
xuddi shunday qilardi, sayt shunga tayanadi.
"""

from fastapi import Request

from .config import get_settings


def resolve_language(request: Request) -> str:
    """`?lang=uz` yoki `Accept-Language` — aks holda asosiy til."""
    s = get_settings()
    lang = (request.query_params.get("lang") or "").lower()
    if lang in s.languages:
        return lang
    header = request.headers.get("accept-language", "")
    for part in header.split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in s.languages:
            return code
    return s.default_language


def tr(obj, field: str, language: str) -> str:
    """`obj.<field>_<lang>`, bo'sh bo'lsa `obj.<field>_ru`."""
    value = getattr(obj, f"{field}_{language}", None) or ""
    if not value:
        value = getattr(obj, f"{field}_{get_settings().default_language}", None) or ""
    return value


def translated(obj, fields: tuple[str, ...], language: str) -> dict:
    """Bir nechta maydonni bir yo'la — javob lug'atiga qo'shish uchun."""
    return {field: tr(obj, field, language) for field in fields}
