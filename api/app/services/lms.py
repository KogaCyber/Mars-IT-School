"""LMS (gamification) bazasidan o'qish — faqat SELECT, faqat kerakli qatorlar.

LMS o'chiq bo'lsa (`LMS_DATABASE_URL` bo'sh yoki ulanib bo'lmadi) sayt
YIQILMAYDI: funksiyalar bo'sh natija qaytaradi, javobda saytdagi zaxira
qiymatlar ishlatiladi (masalan `Teacher.full_name`). Sayt LMS'ga bog'liq, lekin
uning qulashidan o'lmaydi.
"""

import logging
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.lms import LmsCompany, LmsProgram, LmsTeacher, LmsVacancy

logger = logging.getLogger(__name__)


async def _safe(lms: AsyncSession | None, stmt):
    if lms is None:
        return []
    try:
        return (await lms.execute(stmt)).scalars().all()
    except Exception:  # noqa: BLE001 — LMS muammosi saytni to'xtatmasligi kerak
        logger.exception("LMS bazasidan o'qib bo'lmadi")
        return []


async def teacher_names(lms: AsyncSession | None, ids: Iterable[int | None]) -> dict[int, str]:
    """`users_teacher.id` → «Ism Familiya»."""
    wanted = {i for i in ids if i}
    if not wanted:
        return {}
    rows = await _safe(lms, select(LmsTeacher).where(LmsTeacher.id.in_(wanted)))
    return {t.id: t.full_name for t in rows if t.full_name}


async def programs(lms: AsyncSession | None, ids: Iterable[int | None] | None = None) -> dict[int, LmsProgram]:
    """`courses_program` — hammasi (muharrirdagi ro'yxat uchun) yoki berilgan id'lar."""
    stmt = select(LmsProgram).where(LmsProgram.is_active.is_(True))
    if ids is not None:
        wanted = {i for i in ids if i}
        if not wanted:
            return {}
        stmt = stmt.where(LmsProgram.id.in_(wanted))
    return {p.id: p for p in await _safe(lms, stmt.order_by(LmsProgram.name))}


async def companies(lms: AsyncSession | None, ids: Iterable[int | None] | None = None) -> dict[int, LmsCompany]:
    stmt = select(LmsCompany).where(LmsCompany.is_active.is_(True))
    if ids is not None:
        wanted = {i for i in ids if i}
        if not wanted:
            return {}
        stmt = stmt.where(LmsCompany.id.in_(wanted))
    return {c.id: c for c in await _safe(lms, stmt.order_by(LmsCompany.title))}


async def vacancies(lms: AsyncSession | None, ids: Iterable[int | None] | None = None) -> dict[int, LmsVacancy]:
    stmt = select(LmsVacancy).where(LmsVacancy.is_active.is_(True))
    if ids is not None:
        wanted = {i for i in ids if i}
        if not wanted:
            return {}
        stmt = stmt.where(LmsVacancy.id.in_(wanted))
    return {v.id: v for v in await _safe(lms, stmt.order_by(LmsVacancy.id.desc()))}


async def all_teachers(lms: AsyncSession | None) -> list[LmsTeacher]:
    """Muharrirdagi «O'qituvchi» ro'yxati uchun — faol o'qituvchilar."""
    rows = await _safe(
        lms,
        select(LmsTeacher).where(LmsTeacher.is_active.is_(True)).order_by(LmsTeacher.last_name, LmsTeacher.first_name),
    )
    return [t for t in rows if t.full_name]
