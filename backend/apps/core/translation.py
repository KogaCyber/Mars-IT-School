"""Kontent tarjimalari uchun yordamchilar.

Sayt uch tilda ishlaydi (ru / uz / en). Har bir tarjima qilinadigan matn
model'da uch alohida maydon sifatida saqlanadi: `title_ru`, `title_uz`, `title_en`.
Bo'sh tarjima o'rniga asosiy til (ru) qiymati ko'rsatiladi.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

CONTENT_LANGUAGES: list[str] = settings.CONTENT_LANGUAGES
DEFAULT_LANGUAGE: str = settings.DEFAULT_CONTENT_LANGUAGE


def resolve_language(request) -> str:
    """So'rovdan tilni aniqlaydi: `?lang=uz` yoki `Accept-Language` sarlavhasi."""
    if request is None:
        return DEFAULT_LANGUAGE

    lang = (request.query_params.get("lang") if hasattr(request, "query_params") else None) or ""
    if lang.lower() in CONTENT_LANGUAGES:
        return lang.lower()

    header = request.headers.get("Accept-Language", "") if hasattr(request, "headers") else ""
    for part in header.split(","):
        code = part.split(";")[0].strip().lower()[:2]
        if code in CONTENT_LANGUAGES:
            return code

    return DEFAULT_LANGUAGE


class TranslatedModel(models.Model):
    """`tr()` yordamida tanlangan tildagi qiymatni qaytaradigan abstrakt model."""

    class Meta:
        abstract = True

    def tr(self, field: str, language: str = DEFAULT_LANGUAGE) -> str:
        value = getattr(self, f"{field}_{language}", "") or ""
        if not value:
            value = getattr(self, f"{field}_{DEFAULT_LANGUAGE}", "") or ""
        return value


def translated_char(verbose_name, max_length: int = 200, *, required: bool = True):
    """`title_ru` uchun maydon yaratadi (asosiy til — majburiy)."""
    return models.CharField(verbose_name, max_length=max_length, blank=not required)


def translated_char_optional(verbose_name, max_length: int = 200):
    """`title_uz` / `title_en` uchun maydon (bo'sh bo'lsa ru qiymati ishlatiladi)."""
    return models.CharField(verbose_name, max_length=max_length, blank=True)


def translated_text(verbose_name, *, required: bool = True):
    return models.TextField(verbose_name, blank=not required)


# Admin panelda tarjima maydonlarini bitta yig'ma blokka joylash uchun yordamchi.
# Asosiy til (ru) maydonlari asosiy blokda turadi, bu yerda faqat qolgan tillar.
def translation_fieldset(*bases: str, label=_("Tarjimalar (uz / en)")) -> tuple:  # noqa: B008
    fields = tuple(
        f"{base}_{lang}"
        for base in bases
        for lang in CONTENT_LANGUAGES
        if lang != DEFAULT_LANGUAGE
    )
    return (label, {"fields": fields, "classes": ("collapse",)})
