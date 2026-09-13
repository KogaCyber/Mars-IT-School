"""Vizual muharrir API — faqat xodim uchun (Mars ID orqali kirgan).

Muharrir sahifada ishlaydi: matnga bosdi → maydonni uch tilda tahrirladi →
saqladi. Bu router aynan shuni beradi:

  GET   /api/editor/pages                sahifalar va ularning bo'limlari (spec + joriy qiymatlar)
  GET   /api/editor/sections/{key}       bitta bo'lim — barcha tillar, elementlar
  PATCH /api/editor/sections/{key}       maydonlar / elementlar / ko'rinish
  POST  /api/editor/upload               rasm (jpg/png/webp/gif), 5 MB gacha

Har saqlash kontent versiyasini oshiradi — ochiq API keshi shu zahoti
yaroqsiz bo'ladi, sayt yangi matnni oladi.
"""

import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import serialize as ser
from ..auth import require_editor
from ..config import get_settings
from ..db import get_db
from ..deps import public_cache
from ..models import site as m
from ..services import revision
from ..services.sections import PAGES, SECTION_INDEX, SECTIONS

router = APIRouter(prefix="/api/editor", tags=["editor"], dependencies=[Depends(require_editor)])

LANGS = ("ru", "uz", "en")
SECTION_PLAIN = ("button_url", "button2_url", "image", "image2")
ITEM_PLAIN = ("icon_name", "icon", "image", "url")


def _section_columns(spec: dict) -> set[str]:
    """Bo'lim uchun ruxsat etilgan ustunlar: spec'dagi matn maydonlari × tillar + oddiy maydonlar."""
    cols: set[str] = set()
    for field in spec["fields"]:
        if field in SECTION_PLAIN:
            cols.add(field)
        else:
            cols.update(f"{field}_{lang}" for lang in LANGS)
    return cols


def _item_columns(spec: dict) -> set[str]:
    cols: set[str] = {"order", "is_published"}
    for field in spec.get("items") or ():
        if field in ITEM_PLAIN:
            cols.add(field)
        else:
            cols.update(f"{field}_{lang}" for lang in LANGS)
    return cols


def _section_payload(request: Request, sec: m.PageSection, spec: dict) -> dict:
    values = {col: getattr(sec, col) for col in _section_columns(spec)}
    for col in ("image", "image2"):
        if col in values:
            values[f"{col}_url"] = ser.media_url(request, values[col])
    items = []
    for it in sec.items:
        row = {"id": it.id, **{col: getattr(it, col) for col in _item_columns(spec)}}
        for col in ("icon", "image"):
            if col in row:
                row[f"{col}_url"] = ser.media_url(request, row[col])
        items.append(row)
    return {
        "key": sec.key,
        "page": sec.page,
        "order": sec.order,
        "name": spec["name"],
        "hint": spec["hint"],
        "fields": spec["fields"],
        "item_fields": spec.get("items") or [],
        "item_name": spec.get("item_name") or "",
        "hideable": spec.get("hideable", True),
        "is_published": sec.is_published,
        "values": values,
        "items": items,
    }


@router.get("/pages")
async def pages(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        (
            await db.execute(
                select(m.PageSection).options(selectinload(m.PageSection.items)).order_by(m.PageSection.order)
            )
        )
        .scalars()
        .all()
    )
    by_key = {s.key: s for s in rows}
    result = []
    for page in PAGES:
        sections = [
            _section_payload(request, by_key[spec["key"]], spec)
            for spec in SECTIONS
            if spec["page"] == page["key"] and spec["key"] in by_key
        ]
        result.append({**page, "sections": sections})
    return result


@router.get("/sections/{key}")
async def section(key: str, request: Request, db: AsyncSession = Depends(get_db)):
    spec = SECTION_INDEX.get(key)
    if spec is None:
        raise HTTPException(404, "Bunday bo'lim yo'q.")
    sec = (
        await db.execute(
            select(m.PageSection).where(m.PageSection.key == key).options(selectinload(m.PageSection.items))
        )
    ).scalar_one_or_none()
    if sec is None:
        raise HTTPException(404, "Bo'lim hali yaratilmagan (sync-sections).")
    return _section_payload(request, sec, spec)


class ItemIn(BaseModel):
    id: int | None = None
    values: dict[str, str | int | bool | None] = Field(default_factory=dict)


class SectionPatch(BaseModel):
    values: dict[str, str | None] = Field(default_factory=dict)
    is_published: bool | None = None
    items: list[ItemIn] | None = None  # berilsa — ro'yxat TO'LIQ almashtiriladi (tartib = ro'yxat tartibi)


@router.patch("/sections/{key}")
async def update_section(key: str, body: SectionPatch, request: Request, db: AsyncSession = Depends(get_db)):
    spec = SECTION_INDEX.get(key)
    if spec is None:
        raise HTTPException(404, "Bunday bo'lim yo'q.")
    sec = (
        await db.execute(
            select(m.PageSection).where(m.PageSection.key == key).options(selectinload(m.PageSection.items))
        )
    ).scalar_one_or_none()
    if sec is None:
        raise HTTPException(404, "Bo'lim hali yaratilmagan.")

    allowed = _section_columns(spec)
    unknown = set(body.values) - allowed
    if unknown:
        raise HTTPException(400, f"Bu bo'limda bunday maydon yo'q: {', '.join(sorted(unknown))}")
    for col, value in body.values.items():
        setattr(sec, col, (value or "").strip() if isinstance(value, str) else (value or ""))

    if body.is_published is not None and spec.get("hideable", True):
        sec.is_published = body.is_published

    if body.items is not None:
        item_allowed = _item_columns(spec)
        existing = {it.id: it for it in sec.items}
        kept: list[m.SectionItem] = []
        for index, item in enumerate(body.items):
            bad = set(item.values) - item_allowed
            if bad:
                raise HTTPException(400, f"Elementda bunday maydon yo'q: {', '.join(sorted(bad))}")
            obj = existing.get(item.id) if item.id else None
            if obj is None:
                obj = m.SectionItem(section_id=sec.id)
                db.add(obj)
            for col, value in item.values.items():
                if col == "is_published":
                    obj.is_published = bool(value)
                elif col == "order":
                    continue
                else:
                    setattr(obj, col, (value or "").strip() if isinstance(value, str) else (value or ""))
            obj.order = index
            kept.append(obj)
        for old in sec.items:
            if old not in kept:
                await db.delete(old)
        sec.items = kept

    await db.flush()
    await revision.bump(db)
    public_cache.clear()
    await db.refresh(sec, attribute_names=["items"])
    return _section_payload(request, sec, spec)


IMAGE_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".webp": (b"RIFF",),
    ".gif": (b"GIF87a", b"GIF89a"),
}


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), folder: str = "sections"):
    """Rasm: kengaytma, hajm VA mazmun tekshiriladi; nom tasodifiy.

    SVG ataylab yo'q — ichida skript bo'lishi mumkin. `folder` faqat
    harf-raqam: yo'l bo'ylab yurib ketib bo'lmasin.
    """
    s = get_settings()
    if not folder.replace("-", "").replace("_", "").isalnum() or len(folder) > 40:
        raise HTTPException(400, "Noto'g'ri papka nomi.")
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in IMAGE_SIGNATURES:
        raise HTTPException(400, f"Rasm turi mos emas. Ruxsat etilgan: {', '.join(sorted(IMAGE_SIGNATURES))}.")
    data = await file.read(s.max_upload_bytes + 1)
    if len(data) > s.max_upload_bytes:
        raise HTTPException(400, f"Rasm {s.max_upload_bytes // (1024 * 1024)} MB dan oshmasligi kerak.")
    if not data or not any(data.startswith(sig) for sig in IMAGE_SIGNATURES[suffix]):
        raise HTTPException(400, "Fayl mazmuni rasm emas.")

    rel = Path(folder) / f"{secrets.token_hex(12)}{suffix}"
    target = s.media_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": str(rel), "url": ser.media_url(request, str(rel))}
