"""Ochiq (autentifikatsiyasiz) o'qish: bosh sahifa bloklari, sozlamalar, bo'limlar."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import serialize as ser
from ..db import get_db, get_lms
from ..i18n import resolve_language
from ..models import site as m
from ..services import lms as lms_svc
from ..services import revision
from ..services.sections import is_hideable

router = APIRouter(tags=["public"])

HOME_LIMIT = 24


def _published(model, limit: int | None = None):
    stmt = select(model).where(model.is_published.is_(True)).order_by(model.order, model.created_at.desc())
    return stmt.limit(limit) if limit else stmt


async def _list(db: AsyncSession, model, limit: int | None = None):
    return (await db.execute(_published(model, limit))).scalars().all()


# --- oddiy ro'yxatlar --------------------------------------------------------

_SIMPLE = {
    "advantages": (m.Advantage, lambda r, o, lang: ser.advantage(r, o, lang)),
    "reviews": (m.ParentReview, lambda r, o, lang: ser.review(r, o, lang)),
    "faqs": (m.FAQ, lambda r, o, lang: ser.faq(o, lang)),
    "space-features": (m.SpaceFeature, lambda r, o, lang: ser.space_feature(r, o, lang)),
    "statistics": (m.Statistic, lambda r, o, lang: ser.statistic(o, lang)),
    "founders": (m.Founder, lambda r, o, lang: ser.founder(r, o, lang)),
    "future-benefits": (m.FutureBenefit, lambda r, o, lang: ser.future_benefit(r, o, lang)),
    "child-skills": (m.ChildSkill, lambda r, o, lang: ser.child_skill(r, o, lang)),
    "project-defence-steps": (m.ProjectDefenceStep, lambda r, o, lang: ser.project_defence_step(o, lang)),
    "school-features": (m.SchoolFeature, lambda r, o, lang: ser.school_feature(o, lang)),
}


def _make_simple_routes():
    for path, (model, fn) in _SIMPLE.items():

        async def list_view(
            request: Request,
            db: AsyncSession = Depends(get_db),
            lang: str = Depends(resolve_language),
            _model=model,
            _fn=fn,
        ):
            return [_fn(request, o, lang) for o in await _list(db, _model)]

        async def detail_view(
            pk: int,
            request: Request,
            db: AsyncSession = Depends(get_db),
            lang: str = Depends(resolve_language),
            _model=model,
            _fn=fn,
        ):
            obj = (
                await db.execute(select(_model).where(_model.id == pk, _model.is_published.is_(True)))
            ).scalar_one_or_none()
            if obj is None:
                from fastapi import HTTPException

                raise HTTPException(404, "Topilmadi.")
            return _fn(request, obj, lang)

        router.add_api_route(f"/{path}/", list_view, methods=["GET"], name=f"{path}-list")
        router.add_api_route(f"/{path}/{{pk}}/", detail_view, methods=["GET"], name=f"{path}-detail")


_make_simple_routes()


# --- sozlamalar, bo'limlar, bosh sahifa ---------------------------------------


async def _settings(db: AsyncSession) -> m.SiteSettings:
    obj = (await db.execute(select(m.SiteSettings).limit(1))).scalar_one_or_none()
    if obj is None:
        obj = m.SiteSettings()
        db.add(obj)
        await db.flush()
    return obj


@router.get("/site-settings/")
async def site_settings(request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)):
    return ser.site_settings(request, await _settings(db), lang)


async def _sections(db: AsyncSession, request: Request, lang: str, pages: list[str] | None = None) -> dict:
    stmt = (
        select(m.PageSection)
        .options(selectinload(m.PageSection.items))
        .order_by(m.PageSection.order, m.PageSection.key)
    )
    if pages:
        stmt = stmt.where(m.PageSection.page.in_(pages))
    rows = (await db.execute(stmt)).scalars().all()
    return {s.key: ser.page_section(request, s, lang, hideable=is_hideable(s.key)) for s in rows}


@router.get("/content/")
async def content(request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)):
    """Barcha sahifalarning bo'limlari — bitta so'rovda."""
    return await _sections(db, request, lang)


@router.get("/revision/")
async def revision_view(db: AsyncSession = Depends(get_db)):
    return {"revision": await revision.current(db)}


@router.get("/home/")
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
):
    """Bosh sahifa uchun hamma narsa — bitta so'rovda."""
    from datetime import datetime, timezone

    teachers = (
        (
            await db.execute(
                _published(m.Teacher, 12).options(
                    selectinload(m.Teacher.skill_links).selectinload(m.TeacherSkill.skill)
                )
            )
        )
        .scalars()
        .all()
    )
    names = await lms_svc.teacher_names(lms, (t.lms_teacher_id for t in teachers))
    news = (
        (
            await db.execute(
                select(m.News)
                .where(m.News.is_published.is_(True), m.News.published_at <= datetime.now(timezone.utc))
                .options(selectinload(m.News.category))
                .order_by(m.News.published_at.desc())
                .limit(9)
            )
        )
        .scalars()
        .all()
    )

    return {
        "settings": ser.site_settings(request, await _settings(db), lang),
        "sections": await _sections(db, request, lang, ["home", "common"]),
        "advantages": [ser.advantage(request, o, lang) for o in await _list(db, m.Advantage, HOME_LIMIT)],
        "reviews": [ser.review(request, o, lang) for o in await _list(db, m.ParentReview, HOME_LIMIT)],
        "faqs": [ser.faq(o, lang) for o in await _list(db, m.FAQ, HOME_LIMIT)],
        "teachers": [ser.teacher_list(request, t, lang, names.get(t.lms_teacher_id or 0)) for t in teachers],
        "news": [ser.news_list(request, n, lang) for n in news],
    }
