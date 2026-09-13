"""Sahifa bo'limlari reestri va uni baza bilan moslashtirish.

`content/sections.json` — qaysi bo'limlar bor, qaysi sahifada, qaysi maydonlar
tahrirlanadi (vizual muharrir shu ro'yxatga qaraydi). `section_defaults.json` —
maketdagi standart matnlar: bo'lim birinchi marta yaratilganda ular bilan
to'ldiriladi, shunda sayt bo'sh emas.
"""

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.site import PageSection, SectionItem

logger = logging.getLogger(__name__)

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"

with (CONTENT_DIR / "sections.json").open(encoding="utf-8") as fh:
    _SPEC = json.load(fh)

PAGES: list[dict] = _SPEC["pages"]
SECTIONS: list[dict] = _SPEC["sections"]
SECTION_INDEX: dict[str, dict] = {s["key"]: s for s in SECTIONS}


def load_defaults() -> dict:
    path = CONTENT_DIR / "section_defaults.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.exception("section_defaults.json o'qilmadi")
        return {}


def is_hideable(key: str) -> bool:
    return SECTION_INDEX.get(key, {}).get("hideable", True)


_ITEM_FIELDS = {c.name for c in SectionItem.__table__.columns} - {"id", "section_id"}
_SECTION_FIELDS = {c.name for c in PageSection.__table__.columns} - {"id", "key", "page", "order"}


async def sync_sections(db: AsyncSession) -> dict:
    """Reestrdagi bo'limlarni bazaga moslashtiradi: yetishmayotganini yaratadi,
    sahifa/tartibini yangilaydi. Mavjud matnlarga TEGMAYDI."""
    defaults = load_defaults()
    existing = {s.key: s for s in (await db.execute(select(PageSection))).scalars()}
    created = updated = 0

    for spec in SECTIONS:
        key, order = spec["key"], spec["order"]
        section = existing.get(key)
        if section is None:
            section = PageSection(key=key, page=spec["page"], order=order)
            data = defaults.get(key, {})
            for field, value in (data.get("fields") or {}).items():
                if field in _SECTION_FIELDS and value:
                    setattr(section, field, value)
            for index, item in enumerate(data.get("items") or []):
                clean = {f: v for f, v in item.items() if f in _ITEM_FIELDS and v}
                clean.setdefault("order", index)
                section.items.append(SectionItem(**clean))
            db.add(section)
            created += 1
            continue
        if section.page != spec["page"] or section.order != order:
            section.page, section.order = spec["page"], order
            updated += 1

    await db.flush()
    return {"created": created, "updated": updated}
