"""Muharrir — mavjudotlar (entity) CRUD: kontaktlar, filiallar, yangiliklar, vakansiyalar.

Bo'limlar (`editor.py`) — sahifa matni; bu yerda esa ALOHIDA yozuvlar: filial
qo'shish/o'chirish, vakansiya, yangilik, sayt kontaktlari. Frontend formani
`spec` bo'yicha quradi, shuning uchun maydon ro'yxati bir joyda — shu faylda.

Faqat xodim (Mars ID). Har yozishda kontent versiyasi oshadi va ochiq kesh
tozalanadi — sayt darhol yangilanadi.
"""

import re

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from slugify import slugify
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import serialize as ser
from ..auth import require_editor
from ..db import get_db
from ..deps import public_cache
from ..models import site as m
from ..services import revision

router = APIRouter(prefix="/api/editor", tags=["editor-entities"], dependencies=[Depends(require_editor)])

LANGS = ("ru", "uz", "en")


def field(name, kind, label, **extra):
    return {"name": name, "kind": kind, "label": label, **extra}


# Har bir mavjudot: model, maydonlar spec'i, sarlavha uchun asos (slug/nom).
ENTITIES: dict[str, dict] = {
    "branch": {
        "model": m.Branch,
        "title": "Филиалы",
        "singular": "Филиал",
        "name_from": "name_ru",
        "fields": [
            field("name", "translated", "Название"),
            field("address", "translated", "Адрес"),
            field("landmark", "translated", "Ориентир"),
            field("working_hours", "translated", "Часы работы"),
            field("phone", "text", "Телефон"),
            field("cover", "image", "Фото"),
            field("map_url_yandex", "text", "Ссылка Яндекс.Карты"),
            field("map_url_google", "text", "Ссылка Google Maps"),
            field("latitude", "number", "Широта"),
            field("longitude", "number", "Долгота"),
            field("is_main", "bool", "Главный филиал"),
        ],
    },
    "news": {
        "model": m.News,
        "title": "Новости",
        "singular": "Новость",
        "name_from": "title_ru",
        "fields": [
            field("title", "translated", "Заголовок"),
            field("excerpt", "translated", "Краткое описание", long=True),
            field("body", "translated", "Текст", long=True),
            field("cover", "image", "Обложка"),
            field("reading_minutes", "number", "Минут чтения"),
            field("is_featured", "bool", "В избранном"),
        ],
    },
    "vacancy": {
        "model": m.Vacancy,
        "title": "Вакансии",
        "singular": "Вакансия",
        "name_from": "title_ru",
        "fields": [
            field("title", "translated", "Название"),
            field("description", "translated", "Описание", long=True),
            field("requirements", "translated", "Требования", long=True),
            field("conditions", "translated", "Условия", long=True),
            field(
                "employment_type",
                "select",
                "Тип занятости",
                options=[
                    {"value": "full_time", "label": "Полная"},
                    {"value": "part_time", "label": "Частичная"},
                    {"value": "remote", "label": "Удалённо"},
                    {"value": "internship", "label": "Стажировка"},
                ],
            ),
            field("salary_from", "number", "Зарплата от"),
            field("salary_to", "number", "Зарплата до"),
            field("is_open", "bool", "Открыта"),
        ],
    },
}


def _columns(spec: dict) -> set[str]:
    cols = {"is_published", "order"}
    for f in spec["fields"]:
        if f["kind"] == "translated":
            cols.update(f"{f['name']}_{lang}" for lang in LANGS)
        else:
            cols.add(f["name"])
    return cols


def _row(request: Request, obj, spec: dict) -> dict:
    cols = _columns(spec)
    data = {"id": obj.id, "slug": getattr(obj, "slug", None)}
    for c in cols:
        v = getattr(obj, c, None)
        # Decimal/■ JSON uchun sonlarni floatga.
        data[c] = float(v) if c in ("latitude", "longitude") and v is not None else v
    for f in spec["fields"]:
        if f["kind"] == "image":
            data[f"{f['name']}_url"] = ser.media_url(request, getattr(obj, f["name"], ""))
    return data


async def _unique_slug(db: AsyncSession, model, base: str, exclude_id: int | None = None) -> str:
    root = slugify(base) or "item"
    slug = root
    n = 1
    while True:
        stmt = select(model.id).where(model.slug == slug)
        if exclude_id:
            stmt = stmt.where(model.id != exclude_id)
        if (await db.execute(stmt)).scalar_one_or_none() is None:
            return slug
        n += 1
        slug = f"{root}-{n}"


def _spec(kind: str) -> dict:
    spec = ENTITIES.get(kind)
    if spec is None:
        raise HTTPException(404, "Неизвестный тип.")
    return spec


class EntityIn(BaseModel):
    values: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    is_published: bool | None = None


def _apply(obj, spec: dict, values: dict):
    cols = _columns(spec)
    unknown = set(values) - cols - {"slug"}
    if unknown:
        raise HTTPException(400, f"Недопустимые поля: {', '.join(sorted(unknown))}")
    for f in spec["fields"]:
        if f["kind"] in ("number",):
            name = f["name"]
            if name in values:
                v = values[name]
                setattr(obj, name, None if v in ("", None) else v)
    for c, v in values.items():
        if c == "slug" or c not in cols:
            continue
        f = next((x for x in spec["fields"] if x["name"] == c or c.startswith(x["name"] + "_")), None)
        if f and f["kind"] == "number":
            continue
        if f and f["kind"] == "bool":
            setattr(obj, c, bool(v))
        else:
            setattr(obj, c, (v.strip() if isinstance(v, str) else v))


async def _bump(db: AsyncSession):
    await db.flush()
    await revision.bump(db)
    public_cache.clear()


@router.get("/entities/{kind}")
async def list_entities(kind: str, request: Request, db: AsyncSession = Depends(get_db)):
    spec = _spec(kind)
    model = spec["model"]
    rows = (await db.execute(select(model).order_by(model.order, model.id))).scalars().all()
    return {
        "kind": kind,
        "title": spec["title"],
        "singular": spec["singular"],
        "fields": spec["fields"],
        "items": [_row(request, o, spec) for o in rows],
    }


@router.post("/entities/{kind}", status_code=201)
async def create_entity(kind: str, body: EntityIn, request: Request, db: AsyncSession = Depends(get_db)):
    spec = _spec(kind)
    model = spec["model"]
    obj = model()
    _apply(obj, spec, body.values)
    if body.is_published is not None:
        obj.is_published = body.is_published
    base = body.values.get("slug") or getattr(obj, spec["name_from"], "") or spec["singular"]
    obj.slug = await _unique_slug(db, model, str(base))
    db.add(obj)
    await _bump(db)
    await db.refresh(obj)
    return _row(request, obj, spec)


@router.patch("/entities/{kind}/{item_id}")
async def update_entity(kind: str, item_id: int, body: EntityIn, request: Request, db: AsyncSession = Depends(get_db)):
    spec = _spec(kind)
    model = spec["model"]
    obj = (await db.execute(select(model).where(model.id == item_id))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, "Не найдено.")
    _apply(obj, spec, body.values)
    if body.is_published is not None:
        obj.is_published = body.is_published
    if body.values.get("slug"):
        obj.slug = await _unique_slug(db, model, body.values["slug"], exclude_id=obj.id)
    await _bump(db)
    await db.refresh(obj)
    return _row(request, obj, spec)


@router.delete("/entities/{kind}/{item_id}", status_code=204)
async def delete_entity(kind: str, item_id: int, db: AsyncSession = Depends(get_db)):
    spec = _spec(kind)
    model = spec["model"]
    await db.execute(sa_delete(model).where(model.id == item_id))
    await _bump(db)


# ---------------------------------------------------------------------------
# Sayt kontaktlari (bitta yozuv) — «Контакты» sahifasidagi telefon, email, tarmoqlar
# ---------------------------------------------------------------------------

SETTINGS_FIELDS = [
    field("phone", "text", "Телефон"),
    field("extra_phone", "text", "Доп. телефон"),
    field("email", "text", "Email"),
    field("work_hours", "translated", "Часы работы"),
    field("telegram_url", "text", "Telegram"),
    field("instagram_url", "text", "Instagram"),
    field("youtube_url", "text", "YouTube"),
    field("facebook_url", "text", "Facebook"),
    field("space_app_ios_url", "text", "SPACE — App Store"),
    field("space_app_android_url", "text", "SPACE — Google Play"),
    field("privacy_policy_url", "text", "Политика конфиденциальности"),
    field("offer_url", "text", "Оферта"),
    field("promo_video_url", "text", "Промо-видео (ссылка)"),
    field("promo_cover", "image", "Обложка промо"),
]
_SETTINGS_COLS = {
    f"{f['name']}_{lang}" if f["kind"] == "translated" else f["name"]
    for f in SETTINGS_FIELDS
    for lang in (LANGS if f["kind"] == "translated" else ("",))
}


async def _settings(db: AsyncSession) -> m.SiteSettings:
    obj = (await db.execute(select(m.SiteSettings).limit(1))).scalar_one_or_none()
    if obj is None:
        obj = m.SiteSettings()
        db.add(obj)
        await db.flush()
    return obj


@router.get("/site-settings")
async def get_settings(request: Request, db: AsyncSession = Depends(get_db)):
    obj = await _settings(db)
    values = {c: getattr(obj, c) for c in _SETTINGS_COLS}
    values["promo_cover_url"] = ser.media_url(request, obj.promo_cover)
    return {"fields": SETTINGS_FIELDS, "values": values}


@router.patch("/site-settings")
async def patch_settings(body: EntityIn, request: Request, db: AsyncSession = Depends(get_db)):
    obj = await _settings(db)
    unknown = set(body.values) - _SETTINGS_COLS
    if unknown:
        raise HTTPException(400, f"Недопустимые поля: {', '.join(sorted(unknown))}")
    for c, v in body.values.items():
        setattr(obj, c, v.strip() if isinstance(v, str) else v)
    await _bump(db)
    return await get_settings(request, db)


# Rasm yuklashda `.editor` router'idagi endpoint ishlatiladi (/api/editor/upload).
_ = re  # (kelajakda validatsiya uchun)
