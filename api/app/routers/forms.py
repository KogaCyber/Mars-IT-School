"""Saytdan keladigan formalar: ariza, vakansiyaga otklik, test."""

import secrets
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import serialize as ser
from ..config import get_settings
from ..db import get_db
from ..deps import client_ip, rate_limit
from ..i18n import resolve_language, tr, translated
from ..models import site as m
from ..services import quiz as quiz_svc
from ..services.notify import notify_new_lead
from ..validators import validate_uz_phone

router = APIRouter(tags=["forms"])

LEAD_MESSAGE = {
    "ru": "Ваша заявка принята. Мы скоро свяжемся с вами.",
    "uz": "Arizangiz qabul qilindi. Tez orada bog'lanamiz.",
    "en": "Your request has been received. We will contact you shortly.",
}

lead_limit = rate_limit("lead", 40, 3600)


def _detail(lang: str) -> str:
    return LEAD_MESSAGE.get(lang) or LEAD_MESSAGE["ru"]


# ---------------------------------------------------------------------------
# Ariza («Bepul sinov darsiga yozilish»)
# ---------------------------------------------------------------------------


class LeadIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    phone: str = Field(max_length=32)
    course: str | None = None  # kurs slug'i
    branch: str | None = None  # filial slug'i
    child_age: int | None = Field(default=None, ge=3, le=25)
    comment: str = Field(default="", max_length=1000)
    source: str = Field(default="home", max_length=16)
    website: str = ""  # honeypot — odam to'ldirmaydi

    @field_validator("full_name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 2:
            raise ValueError("Ism juda qisqa.")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return validate_uz_phone(v)


@router.post("/leads/", status_code=201, dependencies=[Depends(lead_limit)])
async def create_lead(
    body: LeadIn,
    request: Request,
    background: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
):
    if body.website:
        # Honeypot to'ldirilgan — bot. Sababini aytmaymiz.
        raise HTTPException(400, "So'rovni yuborib bo'lmadi.")

    unresolved: dict[str, str] = {}
    course = branch = None
    if body.course:
        course = (
            await db.execute(select(m.Course).where(m.Course.slug == body.course, m.Course.is_published.is_(True)))
        ).scalar_one_or_none()
        if course is None:
            unresolved["course"] = body.course[:100]
    if body.branch:
        branch = (
            await db.execute(select(m.Branch).where(m.Branch.slug == body.branch, m.Branch.is_published.is_(True)))
        ).scalar_one_or_none()
        if branch is None:
            unresolved["branch"] = body.branch[:100]

    # Bog'lanish topilmasa ARIZA YO'QOLMAYDI: kurs nashrdan olingan yoki nomi
    # o'zgargan bo'lishi mumkin — mijozning telefoni bundan aziz.
    note = ""
    if unresolved:
        pairs = "; ".join(f"{k}={v}" for k, v in sorted(unresolved.items()))
        note = f"Saytda topilmagan bog'lanish: {pairs}. Kurs/filial nashrdan olingan bo'lishi mumkin."

    lead = m.Lead(
        full_name=body.full_name,
        phone=body.phone,
        course_id=course.id if course else None,
        branch_id=branch.id if branch else None,
        child_age=body.child_age,
        comment=body.comment,
        source=body.source,
        admin_note=note,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:300],
    )
    db.add(lead)
    await db.flush()

    background.add_task(
        notify_new_lead,
        body.full_name,
        body.phone,
        tr(course, "title", "ru") if course else (body.course or ""),
        body.source,
        body.comment,
    )
    return {"detail": _detail(lang)}


# ---------------------------------------------------------------------------
# Vakansiyaga otklik — rezyume bilan
# ---------------------------------------------------------------------------

RESUME_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF",),
    ".docx": (b"PK\x03\x04",),
    ".doc": (b"\xd0\xcf\x11\xe0", b"{\\rtf"),
    ".rtf": (b"{\\rtf",),
}


async def _store_resume(upload: UploadFile) -> str:
    """Kengaytma, hajm VA mazmun (magic number) tekshiriladi; nom tasodifiy.

    `cv.pdf` deb nomlangan HTML ichida skript bo'lishi mumkin — shuning uchun
    faylning dastlabki baytlari ham tekshiriladi. Nomzodning ismi na diskda,
    na manzilda ko'rinmaydi.
    """
    s = get_settings()
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in RESUME_SIGNATURES:
        raise HTTPException(400, f"Fayl turi mos emas. Ruxsat etilgan: {', '.join(sorted(RESUME_SIGNATURES))}.")
    data = await upload.read(s.max_upload_bytes + 1)
    if len(data) > s.max_upload_bytes:
        raise HTTPException(400, f"Fayl hajmi {s.max_upload_bytes // (1024 * 1024)} MB dan oshmasligi kerak.")
    if not data:
        raise HTTPException(400, "Fayl bo'sh.")
    if not any(data.startswith(magic) for magic in RESUME_SIGNATURES[suffix]):
        raise HTTPException(400, "Fayl mazmuni uning turiga mos kelmadi.")

    now = datetime.now()
    rel = Path("resumes") / f"{now:%Y}" / f"{now:%m}" / f"{secrets.token_hex(16)}{suffix}"
    target = s.private_media_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(rel)


@router.post("/vacancy-applications/", status_code=201, dependencies=[Depends(lead_limit)])
async def apply_vacancy(
    request: Request,
    vacancy: str = Form(...),
    full_name: str = Form(..., max_length=120),
    phone: str = Form(..., max_length=32),
    email: str = Form("", max_length=254),
    cover_letter: str = Form("", max_length=5000),
    resume_url: str = Form("", max_length=300),
    website: str = Form(""),
    resume: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
):
    if website:
        raise HTTPException(400, "So'rovni yuborib bo'lmadi.")
    full_name = " ".join(full_name.split())
    if len(full_name) < 2:
        raise HTTPException(422, "Ism juda qisqa.")
    try:
        phone = validate_uz_phone(phone)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    v = (
        await db.execute(
            select(m.Vacancy).where(
                m.Vacancy.slug == vacancy, m.Vacancy.is_published.is_(True), m.Vacancy.is_open.is_(True)
            )
        )
    ).scalar_one_or_none()
    if v is None:
        raise HTTPException(422, "Vakansiya topilmadi yoki yopilgan.")

    stored = await _store_resume(resume) if resume and resume.filename else ""
    db.add(
        m.VacancyApplication(
            vacancy_id=v.id,
            full_name=full_name,
            phone=phone,
            email=email,
            cover_letter=cover_letter,
            resume=stored,
            resume_url=resume_url,
            ip_address=client_ip(request),
        )
    )
    return {"detail": _detail(lang)}


# ---------------------------------------------------------------------------
# Proforientatsiya testi
# ---------------------------------------------------------------------------


def _quiz_payload(request: Request, quiz: m.Quiz, lang: str) -> dict:
    import random

    questions = []
    for q in quiz_svc.sample_questions(quiz):
        options = list(q.options)
        random.shuffle(options)  # noqa: S311
        questions.append(
            {
                "id": q.id,
                "image": ser.media_url(request, q.image),
                "order": q.order,
                "options": [{"id": o.id, "order": o.order, **translated(o, ("text",), lang)} for o in options],
                **translated(q, ("text",), lang),
            }
        )
    return {
        "id": quiz.id,
        "slug": quiz.slug,
        "questions": questions,
        **translated(quiz, ("title", "description"), lang),
    }


def _quiz_stmt():
    return (
        select(m.Quiz)
        .where(m.Quiz.is_published.is_(True))
        .options(selectinload(m.Quiz.questions).selectinload(m.Question.options), selectinload(m.Quiz.outcomes))
    )


@router.get("/quizzes/")
async def quizzes(request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)):
    rows = (await db.execute(_quiz_stmt().order_by(m.Quiz.order))).scalars().all()
    return [_quiz_payload(request, q, lang) for q in rows]


@router.get("/quizzes/{slug}/")
async def quiz_detail(
    slug: str, request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)
):
    quiz = (await db.execute(_quiz_stmt().where(m.Quiz.slug == slug))).scalar_one_or_none()
    if quiz is None:
        raise HTTPException(404, "Topilmadi.")
    return _quiz_payload(request, quiz, lang)


class SubmissionIn(BaseModel):
    answers: dict[str, str] = Field(min_length=1, max_length=100)
    full_name: str = Field(default="", max_length=120)
    phone: str = Field(default="", max_length=32)

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return validate_uz_phone(v) if v else ""

    @field_validator("answers", mode="before")
    @classmethod
    def _answers(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Javoblar yaroqsiz.")
        cleaned = {str(k): str(val) for k, val in v.items() if str(k).isdigit() and int(k) > 0}
        if not cleaned:
            raise ValueError("Javoblar yaroqsiz.")
        return cleaned


async def _outcome_payload(request: Request, db: AsyncSession, outcome: m.Outcome | None, lang: str) -> dict | None:
    if outcome is None:
        return None
    courses = (
        (
            await db.execute(
                select(m.Course)
                .join(m.OutcomeCourse, m.OutcomeCourse.course_id == m.Course.id)
                .where(m.OutcomeCourse.outcome_id == outcome.id, m.Course.is_published.is_(True))
                .order_by(m.Course.order)
            )
        )
        .scalars()
        .all()
    )
    return {
        "id": outcome.id,
        "code": outcome.code,
        "image": ser.media_url(request, outcome.image),
        "courses": [
            {
                "id": c.id,
                "slug": c.slug,
                "title": tr(c, "title", lang),
                "card_image": ser.media_url(request, c.card_image),
            }
            for c in courses
        ],
        **translated(outcome, ("title", "description"), lang),
    }


async def _result_payload(request: Request, db: AsyncSession, sub: m.Submission, lang: str) -> dict:
    quiz = (
        await db.execute(select(m.Quiz).where(m.Quiz.id == sub.quiz_id).options(selectinload(m.Quiz.outcomes)))
    ).scalar_one()
    outcome = next((o for o in quiz.outcomes if o.id == sub.outcome_id), None)
    scores = {str(k): v for k, v in (sub.scores or {}).items()}
    total = sum(scores.get(str(o.id), 0) for o in quiz.outcomes)
    matches = [
        {
            "code": o.code,
            "title": tr(o, "title", lang),
            "score": scores.get(str(o.id), 0),
            "percent": round(scores.get(str(o.id), 0) * 100 / total) if total else 0,
        }
        for o in quiz.outcomes
    ]
    if matches and total:
        leader = max(matches, key=lambda x: x["score"])
        leader["percent"] += 100 - sum(x["percent"] for x in matches)
    skills = sorted(
        (
            {"code": code, "title": quiz_svc.skill_label(code, lang), "percent": int(p)}
            for code, p in (sub.skills or {}).items()
            if code in quiz_svc.SKILL_LABELS
        ),
        key=lambda x: x["percent"],
        reverse=True,
    )
    return {
        "token": sub.public_token,
        "outcome": await _outcome_payload(request, db, outcome, lang),
        "matches": matches,
        "skills": skills,
        "scores": sub.scores,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


@router.post("/quizzes/{slug}/submit/", status_code=201, dependencies=[Depends(lead_limit)])
async def quiz_submit(
    slug: str,
    body: SubmissionIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(resolve_language),
):
    quiz = (await db.execute(_quiz_stmt().where(m.Quiz.slug == slug))).scalar_one_or_none()
    if quiz is None:
        raise HTTPException(404, "Topilmadi.")
    question_ids = {int(k) for k in body.answers}
    options = [o for q in quiz.questions if q.id in question_ids for o in q.options]
    sub = quiz_svc.evaluate(quiz, options, list(quiz.outcomes), body.answers)
    sub.full_name, sub.phone = body.full_name, body.phone
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return await _result_payload(request, db, sub, lang)


result_limit = rate_limit("result", 30, 60)


@router.get("/quiz-results/{token}/", dependencies=[Depends(result_limit)])
async def quiz_result(
    token: str, request: Request, db: AsyncSession = Depends(get_db), lang: str = Depends(resolve_language)
):
    sub = (await db.execute(select(m.Submission).where(m.Submission.public_token == token))).scalar_one_or_none()
    if sub is None:
        raise HTTPException(404, "Topilmadi.")
    from fastapi.responses import JSONResponse

    payload = await _result_payload(request, db, sub, lang)
    # Shaxsiy havola — CDN/proksi keshlamasin, Referer orqali sizmasin.
    return JSONResponse(payload, headers={"Cache-Control": "no-store, private", "Referrer-Policy": "no-referrer"})
