"""Kurslar, o'qituvchilar, filiallar, yangiliklar, vakansiyalar — o'qish."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import serialize as ser
from ..db import get_db, get_lms
from ..i18n import resolve_language
from ..models import site as m
from ..services import lms as lms_svc

router = APIRouter(tags=["catalog"])


def _404():
    return HTTPException(status_code=404, detail="Topilmadi.")


def _ilike(*columns, term: str):
    pattern = f"%{term}%"
    return or_(*(c.ilike(pattern) for c in columns))


# ---------------------------------------------------------------------------
# Kurslar
# ---------------------------------------------------------------------------


@router.get("/directions/")
async def directions(request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)):
    rows = (
        (
            await db.execute(
                select(m.Direction)
                .where(m.Direction.is_published.is_(True))
                .order_by(m.Direction.order, m.Direction.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    return [ser.direction(request, d, lang) for d in rows]


@router.get("/courses/")
async def courses(
    request: Request,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
    direction: str | None = None,
    age: int | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    search: str | None = None,
    ordering: str | None = None,
):
    stmt = select(m.Course).where(m.Course.is_published.is_(True)).options(selectinload(m.Course.direction))
    if direction:
        stmt = stmt.join(m.Direction).where(m.Direction.slug == direction)
    if age is not None:
        stmt = stmt.where(m.Course.age_from <= age, m.Course.age_to >= age)
    if min_age is not None:
        stmt = stmt.where(m.Course.age_to >= min_age)
    if max_age is not None:
        stmt = stmt.where(m.Course.age_from <= max_age)
    if search:
        stmt = stmt.where(_ilike(m.Course.title_ru, m.Course.subtitle_ru, m.Course.description_ru, term=search))
    order_map = {"order": m.Course.order, "price": m.Course.price, "created_at": m.Course.created_at}
    if ordering and ordering.lstrip("-") in order_map:
        col = order_map[ordering.lstrip("-")]
        stmt = stmt.order_by(col.desc() if ordering.startswith("-") else col)
    else:
        stmt = stmt.order_by(m.Course.order, m.Course.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [ser.course_list(request, c, lang) for c in rows]


@router.get("/courses/{slug}/")
async def course_detail(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
):
    stmt = (
        select(m.Course)
        .where(m.Course.slug == slug, m.Course.is_published.is_(True))
        .options(
            selectinload(m.Course.direction),
            selectinload(m.Course.features),
            selectinload(m.Course.stages),
            selectinload(m.Course.faqs),
            selectinload(m.Course.teacher_links),
        )
    )
    course = (await db.execute(stmt)).scalar_one_or_none()
    if course is None:
        raise _404()
    teacher_ids = [link.teacher_id for link in course.teacher_links]
    teachers = []
    if teacher_ids:
        teachers = (
            (
                await db.execute(
                    select(m.Teacher)
                    .where(m.Teacher.id.in_(teacher_ids), m.Teacher.is_published.is_(True))
                    .options(selectinload(m.Teacher.skill_links).selectinload(m.TeacherSkill.skill))
                    .order_by(m.Teacher.order)
                )
            )
            .scalars()
            .all()
        )
    names = await lms_svc.teacher_names(lms, (t.lms_teacher_id for t in teachers))
    return ser.course_detail(
        request, course, lang, [ser.teacher_list(request, t, lang, names.get(t.lms_teacher_id or 0)) for t in teachers]
    )


# ---------------------------------------------------------------------------
# O'qituvchilar — ism LMS'dan
# ---------------------------------------------------------------------------


def _teachers_stmt():
    return (
        select(m.Teacher)
        .where(m.Teacher.is_published.is_(True))
        .options(selectinload(m.Teacher.skill_links).selectinload(m.TeacherSkill.skill))
        .order_by(m.Teacher.order, m.Teacher.created_at.desc())
    )


@router.get("/teachers/")
async def teachers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
    search: str | None = None,
):
    stmt = _teachers_stmt()
    if search:
        stmt = stmt.where(_ilike(m.Teacher.full_name, m.Teacher.position_ru, m.Teacher.company, term=search))
    rows = (await db.execute(stmt)).scalars().all()
    names = await lms_svc.teacher_names(lms, (t.lms_teacher_id for t in rows))
    return [ser.teacher_list(request, t, lang, names.get(t.lms_teacher_id or 0)) for t in rows]


@router.get("/teachers/{slug}/")
async def teacher_detail(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
):
    teacher = (await db.execute(_teachers_stmt().where(m.Teacher.slug == slug))).scalar_one_or_none()
    if teacher is None:
        raise _404()
    courses_ = (
        (
            await db.execute(
                select(m.Course)
                .join(m.CourseTeacher, m.CourseTeacher.course_id == m.Course.id)
                .where(m.CourseTeacher.teacher_id == teacher.id, m.Course.is_published.is_(True))
                .order_by(m.Course.order)
            )
        )
        .scalars()
        .all()
    )
    names = await lms_svc.teacher_names(lms, [teacher.lms_teacher_id])
    return ser.teacher_detail(request, teacher, lang, courses_, names.get(teacher.lms_teacher_id or 0))


# ---------------------------------------------------------------------------
# Filiallar
# ---------------------------------------------------------------------------


@router.get("/branches/")
async def branches(
    request: Request,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
    search: str | None = None,
):
    stmt = select(m.Branch).where(m.Branch.is_published.is_(True)).order_by(m.Branch.order, m.Branch.created_at.desc())
    if search:
        stmt = stmt.where(_ilike(m.Branch.name_ru, m.Branch.address_ru, term=search))
    rows = (await db.execute(stmt)).scalars().all()
    return [ser.branch_list(request, b, lang) for b in rows]


@router.get("/branches/{slug}/")
async def branch_detail(
    slug: str, request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)
):
    branch = (
        await db.execute(
            select(m.Branch)
            .where(m.Branch.slug == slug, m.Branch.is_published.is_(True))
            .options(selectinload(m.Branch.gallery))
        )
    ).scalar_one_or_none()
    if branch is None:
        raise _404()
    return ser.branch_detail(request, branch, lang)


# ---------------------------------------------------------------------------
# Yangiliklar — sahifalangan ro'yxat (Django DRF shakli)
# ---------------------------------------------------------------------------


@router.get("/news-categories/")
async def news_categories(db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)):
    rows = (
        (
            await db.execute(
                select(m.NewsCategory).where(m.NewsCategory.is_published.is_(True)).order_by(m.NewsCategory.order)
            )
        )
        .scalars()
        .all()
    )
    return [ser.news_category(c, lang) for c in rows]


def _news_stmt():
    return (
        select(m.News)
        .where(m.News.is_published.is_(True), m.News.published_at <= datetime.now(timezone.utc))
        .options(selectinload(m.News.category))
    )


@router.get("/news/")
async def news(
    request: Request,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
    category__slug: str | None = None,
    is_featured: bool | None = None,
    search: str | None = None,
    ordering: str | None = None,
):
    stmt = _news_stmt()
    if category__slug:
        stmt = stmt.join(m.NewsCategory).where(m.NewsCategory.slug == category__slug)
    if is_featured is not None:
        stmt = stmt.where(m.News.is_featured.is_(is_featured))
    if search:
        stmt = stmt.where(_ilike(m.News.title_ru, m.News.excerpt_ru, m.News.body_ru, term=search))
    order_map = {"published_at": m.News.published_at, "views_count": m.News.views_count}
    if ordering and ordering.lstrip("-") in order_map:
        col = order_map[ordering.lstrip("-")]
        stmt = stmt.order_by(col.desc() if ordering.startswith("-") else col)
    else:
        stmt = stmt.order_by(m.News.order, m.News.published_at.desc())

    total = (await db.execute(select(func.count()).select_from(stmt.order_by(None).subquery()))).scalar() or 0
    rows = (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    def page_url(n: int | None) -> str | None:
        if n is None:
            return None
        return str(request.url.include_query_params(page=n))

    has_next = page * page_size < total
    return {
        "count": total,
        "next": page_url(page + 1) if has_next else None,
        "previous": page_url(page - 1) if page > 1 else None,
        "results": [ser.news_list(request, n, lang) for n in rows],
    }


@router.get("/news/{slug}/")
async def news_detail(
    slug: str, request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)
):
    item = (
        await db.execute(_news_stmt().where(m.News.slug == slug).options(selectinload(m.News.gallery)))
    ).scalar_one_or_none()
    if item is None:
        raise _404()
    # Ko'rishlar soni — poyga holatisiz (bazada `+ 1`). Ob'ektni QO'LDA
    # o'zgartirmaymiz: aks holda commit'da ikkinchi UPDATE ketib, +2 bo'lardi.
    await db.execute(update(m.News).where(m.News.id == item.id).values(views_count=m.News.views_count + 1))
    await db.refresh(item, attribute_names=["views_count"])
    return ser.news_detail(request, item, lang)


# ---------------------------------------------------------------------------
# Vakansiyalar — uz/ru matnlar LMS'dan (bo'lsa), qolgani saytdan
# ---------------------------------------------------------------------------


async def _with_lms_texts(lms: AsyncSession | None, rows: list[m.Vacancy]) -> list[m.Vacancy]:
    """LMS'da bog'langan vakansiya bo'lsa, uz/ru matnlar UNDAN olinadi."""
    linked = await lms_svc.vacancies(lms, (v.lms_vacancy_id for v in rows))
    for v in rows:
        src = linked.get(v.lms_vacancy_id or 0)
        if src is None:
            continue
        for field in ("title", "description", "requirements"):
            for lang in ("uz", "ru"):
                value = getattr(src, f"{field}_{lang}", None)
                if value:
                    setattr(v, f"{field}_{lang}", value)
    return rows


@router.get("/vacancies/")
async def vacancies(
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
    search: str | None = None,
):
    stmt = (
        select(m.Vacancy)
        .where(m.Vacancy.is_published.is_(True), m.Vacancy.is_open.is_(True))
        .options(selectinload(m.Vacancy.branch))
        .order_by(m.Vacancy.order, m.Vacancy.created_at.desc())
    )
    if search:
        stmt = stmt.where(_ilike(m.Vacancy.title_ru, m.Vacancy.description_ru, term=search))
    rows = await _with_lms_texts(lms, list((await db.execute(stmt)).scalars().all()))
    return [ser.vacancy(v, lang) for v in rows]


@router.get("/vacancies/{slug}/")
async def vacancy_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
    lms: AsyncSession | None = Depends(get_lms),
    lang: str = Depends(resolve_language),
):
    v = (
        await db.execute(
            select(m.Vacancy)
            .where(m.Vacancy.slug == slug, m.Vacancy.is_published.is_(True), m.Vacancy.is_open.is_(True))
            .options(selectinload(m.Vacancy.branch))
        )
    ).scalar_one_or_none()
    if v is None:
        raise _404()
    await _with_lms_texts(lms, [v])
    return ser.vacancy(v, lang)
