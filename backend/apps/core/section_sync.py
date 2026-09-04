"""Reestrdagi bo'limlarni ma'lumotlar bazasi bilan moslashtirish.

`sections.py` — bo'limlar ro'yxati, baza esa ularning kontentini saqlaydi.
Sinxronizatsiya yetishmayotgan yozuvlarni yaratadi, tartibini va sahifasini
yangilaydi hamda reestrdan olib tashlangan bo'limlarni belgilab qo'yadi.

Birinchi yaratilishda yozuv `fixtures/section_defaults.json` dagi matn bilan
to'ldiriladi — bu maketdagi joriy matnlar. Shu tufayli admin panel bo'sh emas:
kontent kirituvchi odam saytda turgan matnni ko'radi va uni tahrirlaydi.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from .sections import SECTION_ORDER, SECTIONS

logger = logging.getLogger(__name__)

DEFAULTS_PATH = Path(__file__).resolve().parent / "fixtures" / "section_defaults.json"


def load_defaults() -> dict:
    """Maketdagi standart matnlar (frontenddan eksport qilingan)."""
    if not DEFAULTS_PATH.exists():
        return {}
    try:
        return json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.exception("section_defaults.json o'qilmadi")
        return {}


def sync_sections(*, stdout=None) -> dict:
    """Reestrni bazaga moslashtiradi. Qaytaradi: {'created': n, 'updated': n}."""
    from .models import PageSection, SectionItem

    defaults = load_defaults()
    created = updated = 0

    existing = {section.key: section for section in PageSection.objects.all()}

    for spec in SECTIONS:
        key = spec["key"]
        order = SECTION_ORDER[key]
        section = existing.get(key)

        if section is None:
            section = PageSection(key=key, page=spec["page"], order=order)
            _apply_defaults(section, defaults.get(key, {}))
            section.save()
            _create_items(SectionItem, section, defaults.get(key, {}).get("items", []))
            created += 1
            if stdout:
                stdout.write(f"  + {key}")
            continue

        if section.page != spec["page"] or section.order != order:
            section.page = spec["page"]
            section.order = order
            section.save(update_fields=["page", "order"])
            updated += 1

    return {"created": created, "updated": updated}


def _apply_defaults(section, data: dict) -> None:
    for field, value in (data.get("fields") or {}).items():
        if hasattr(section, field) and value:
            setattr(section, field, value)


def _create_items(item_model, section, items: list) -> None:
    for index, data in enumerate(items):
        fields = {
            field: value
            for field, value in data.items()
            if value and field in {f.name for f in item_model._meta.get_fields()}
        }
        item_model.objects.create(section=section, order=index * 10, **fields)


def sync_quietly() -> None:
    """Admin ro'yxati ochilganda chaqiriladi — yangi bo'lim darrov ko'rinsin.

    Xato (masalan baza vaqtincha yetib bo'lmasa) admin panelni buzmasligi kerak,
    shuning uchun jimgina qayd etiladi.
    """
    if not getattr(settings, "SECTIONS_AUTOSYNC", True):
        return
    try:
        sync_sections()
    except Exception:  # noqa: BLE001
        logger.exception("Sahifa bo'limlarini sinxronlab bo'lmadi")
