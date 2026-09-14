"""Javob lug'atlarini yasash — eski Django API bilan AYNAN bir xil shakl.

Sayt (Vue) shu maydonlarga tayanadi; bu yerdagi nomlar va tuzilma
`backend/apps/*/serializers.py` (Django) dan ko'chirilgan. Yangi maydon
qo'shish mumkin, borini o'zgartirish — sayt buziladi.
"""

from decimal import Decimal

from fastapi import Request

from .config import get_settings
from .i18n import tr, translated
from .models import site as m

# ---------------------------------------------------------------------------
# Rasmlar: bazada nisbiy yo'l, javobda to'liq URL
# ---------------------------------------------------------------------------


def media_url(request: Request, path: str | None) -> str | None:
    """`courses/abc.webp` → `https://core.marsit.uz/school/media/courses/abc.webp`."""
    if not path:
        return None
    s = get_settings()
    # `request.base_url` proksi ortida ALLAQACHON `root_path` (`/school`) ni o'z
    # ichiga oladi — xuddi `auth._redirect_uri` dagidek. Shu sababli `root_path`
    # ni QAYTA qo'shmaymiz: aks holda `/school/school/media/...` bo'lib, nginx
    # uni media deb topmaydi (SPA'ga tushib, rasm o'rniga HTML qaytaradi).
    base = str(request.base_url).rstrip("/")
    media = s.public_media_url.strip("/")
    return f"{base}/{media}/{path.lstrip('/')}"


def _price(value: Decimal | None) -> str | None:
    # Django DecimalField JSON'da satr sifatida chiqardi ("800000") — sayt shuni kutadi.
    return None if value is None else f"{value:.0f}"


def _num(value) -> float | None:
    return None if value is None else float(value)


# ---------------------------------------------------------------------------
# Kurslar
# ---------------------------------------------------------------------------


def course_list(request: Request, c: m.Course, lang: str) -> dict:
    return {
        "id": c.id,
        "slug": c.slug,
        "card_image": media_url(request, c.card_image),
        "accent_color": c.accent_color,
        "age_from": c.age_from,
        "age_to": c.age_to,
        "age_range": f"{c.age_from}–{c.age_to}",
        "duration_months": c.duration_months,
        "lessons_per_week": c.lessons_per_week,
        "price": _price(c.price),
        "is_featured": c.is_featured,
        "direction": c.direction.slug if c.direction else None,
        **translated(c, ("title", "subtitle"), lang),
    }


def course_detail(request: Request, c: m.Course, lang: str, teachers: list[dict]) -> dict:
    data = course_list(request, c, lang)
    data.update(
        {
            "description": tr(c, "description", lang),
            "hero_image": media_url(request, c.hero_image),
            "lesson_duration_minutes": c.lesson_duration_minutes,
            "teachers": teachers,
            "features": [
                {
                    "id": f.id,
                    "icon": media_url(request, f.icon),
                    "order": f.order,
                    **translated(f, ("title", "description"), lang),
                }
                for f in c.features
            ],
            "stages": [
                {
                    "id": st.id,
                    "number": st.number,
                    "image": media_url(request, st.image),
                    "duration_months": st.duration_months,
                    "order": st.order,
                    **translated(st, ("title", "description"), lang),
                }
                for st in c.stages
            ],
            "faqs": [{"id": f.id, "order": f.order, **translated(f, ("question", "answer"), lang)} for f in c.faqs],
        }
    )
    return data


def direction(request: Request, d: m.Direction, lang: str) -> dict:
    return {
        "id": d.id,
        "slug": d.slug,
        "icon": media_url(request, d.icon),
        **translated(d, ("title", "description"), lang),
    }


# ---------------------------------------------------------------------------
# O'qituvchilar
# ---------------------------------------------------------------------------


def teacher_list(request: Request, t: m.Teacher, lang: str, lms_name: str | None = None) -> dict:
    return {
        "id": t.id,
        "slug": t.slug,
        # Ism LMS'dan (`users_teacher`); LMS o'chiq bo'lsa — saytdagi zaxira.
        "full_name": lms_name or t.full_name,
        "photo": media_url(request, t.photo),
        "badge": t.badge,
        "company": t.company,
        "company_logo": media_url(request, t.company_logo),
        "experience_years": t.experience_years,
        "students_count": t.students_count,
        "skills": [
            {"id": link.skill.id, "name": link.skill.name, "icon": media_url(request, link.skill.icon)}
            for link in t.skill_links
        ],
        **translated(t, ("position", "bio"), lang),
    }


def teacher_detail(
    request: Request, t: m.Teacher, lang: str, courses: list[m.Course], lms_name: str | None = None
) -> dict:
    data = teacher_list(request, t, lang, lms_name)
    data.update(
        {
            "telegram_url": t.telegram_url,
            "linkedin_url": t.linkedin_url,
            "instagram_url": t.instagram_url,
            "courses": [{"id": c.id, "slug": c.slug, "title": tr(c, "title", lang)} for c in courses],
        }
    )
    return data


# ---------------------------------------------------------------------------
# Filiallar
# ---------------------------------------------------------------------------


def branch_list(request: Request, b: m.Branch, lang: str) -> dict:
    return {
        "id": b.id,
        "slug": b.slug,
        "phone": b.phone,
        "latitude": _num(b.latitude),
        "longitude": _num(b.longitude),
        "map_url_yandex": b.map_url_yandex,
        "map_url_google": b.map_url_google,
        "cover": media_url(request, b.cover),
        "is_main": b.is_main,
        **translated(b, ("name", "address", "landmark", "working_hours"), lang),
    }


def branch_detail(request: Request, b: m.Branch, lang: str) -> dict:
    data = branch_list(request, b, lang)
    data["gallery"] = [{"id": g.id, "image": media_url(request, g.image), "order": g.order} for g in b.gallery]
    return data


# ---------------------------------------------------------------------------
# Yangiliklar
# ---------------------------------------------------------------------------


def news_category(n: m.NewsCategory, lang: str) -> dict:
    return {"id": n.id, "slug": n.slug, **translated(n, ("title",), lang)}


def news_list(request: Request, n: m.News, lang: str) -> dict:
    return {
        "id": n.id,
        "slug": n.slug,
        "cover": media_url(request, n.cover),
        "category": news_category(n.category, lang) if n.category else None,
        "published_at": n.published_at.isoformat() if n.published_at else None,
        "reading_minutes": n.reading_minutes,
        "views_count": n.views_count,
        "is_featured": n.is_featured,
        **translated(n, ("title", "excerpt"), lang),
    }


def news_detail(request: Request, n: m.News, lang: str) -> dict:
    data = news_list(request, n, lang)
    data["body"] = tr(n, "body", lang)
    data["gallery"] = [
        {
            "id": g.id,
            "image": media_url(request, g.image),
            "order": g.order,
            **translated(g, ("caption",), lang),
        }
        for g in n.gallery
    ]
    return data


# ---------------------------------------------------------------------------
# Vakansiyalar
# ---------------------------------------------------------------------------


def vacancy(v: m.Vacancy, lang: str) -> dict:
    return {
        "id": v.id,
        "slug": v.slug,
        "employment_type": v.employment_type,
        "salary_from": v.salary_from,
        "salary_to": v.salary_to,
        "salary_currency": v.salary_currency,
        "is_open": v.is_open,
        "branch_name": tr(v.branch, "name", lang) if v.branch else "",
        "icon_name": v.icon_name,
        **translated(v, ("title", "description", "requirements", "conditions"), lang),
    }


# ---------------------------------------------------------------------------
# Bosh sahifa bloklari va sozlamalar
# ---------------------------------------------------------------------------


def site_settings(request: Request, s: m.SiteSettings, lang: str) -> dict:
    return {
        "phone": s.phone,
        "extra_phone": s.extra_phone,
        "email": s.email,
        "telegram_url": s.telegram_url,
        "instagram_url": s.instagram_url,
        "youtube_url": s.youtube_url,
        "facebook_url": s.facebook_url,
        "space_app_ios_url": s.space_app_ios_url,
        "space_app_android_url": s.space_app_android_url,
        "privacy_policy_url": s.privacy_policy_url,
        "offer_url": s.offer_url,
        "promo_video_url": s.promo_video_url,
        "promo_video": media_url(request, s.promo_video),
        "promo_cover": media_url(request, s.promo_cover),
        "work_hours": tr(s, "work_hours", lang),
    }


def advantage(request: Request, a: m.Advantage, lang: str) -> dict:
    return {
        "id": a.id,
        "number": a.number,
        "image": media_url(request, a.image),
        **translated(a, ("title", "description"), lang),
    }


def review(request: Request, r: m.ParentReview, lang: str) -> dict:
    return {
        "id": r.id,
        "full_name": r.full_name,
        "photo": media_url(request, r.photo),
        "video_url": r.video_url,
        **translated(r, ("text", "relation"), lang),
    }


def faq(f: m.FAQ, lang: str) -> dict:
    return {"id": f.id, **translated(f, ("question", "answer"), lang)}


def space_feature(request: Request, f: m.SpaceFeature, lang: str) -> dict:
    return {
        "id": f.id,
        "icon": media_url(request, f.icon),
        "screenshot": media_url(request, f.screenshot),
        **translated(f, ("title", "description"), lang),
    }


def statistic(s: m.Statistic, lang: str) -> dict:
    return {"id": s.id, "value": s.value, **translated(s, ("label",), lang)}


def founder(request: Request, f: m.Founder, lang: str) -> dict:
    return {
        "id": f.id,
        "full_name": f.full_name,
        "photo": media_url(request, f.photo),
        **translated(f, ("position", "bio"), lang),
    }


def future_benefit(request: Request, f: m.FutureBenefit, lang: str) -> dict:
    return {"id": f.id, "icon": media_url(request, f.icon), **translated(f, ("title", "description"), lang)}


def child_skill(request: Request, c: m.ChildSkill, lang: str) -> dict:
    return {
        "id": c.id,
        "icon": media_url(request, c.icon),
        "icon_name": c.icon_name,
        **translated(c, ("title", "description"), lang),
    }


def project_defence_step(p: m.ProjectDefenceStep, lang: str) -> dict:
    return {"id": p.id, "icon_name": p.icon_name, **translated(p, ("title", "description", "label"), lang)}


def school_feature(f: m.SchoolFeature, lang: str) -> dict:
    return {"id": f.id, **translated(f, ("title",), lang)}


# ---------------------------------------------------------------------------
# Sahifa bo'limlari
# ---------------------------------------------------------------------------

SECTION_TR = ("eyebrow", "title", "subtitle", "text", "note", "button_label", "button2_label")
ITEM_TR = ("value", "label", "title", "text", "note", "list")


def section_item(request: Request, it: m.SectionItem, lang: str) -> dict:
    return {
        "id": it.id,
        "order": it.order,
        "icon_name": it.icon_name,
        "icon": media_url(request, it.icon),
        "image": media_url(request, it.image),
        "url": it.url,
        **translated(it, ITEM_TR, lang),
    }


def page_section(request: Request, sec: m.PageSection, lang: str, hideable: bool = True) -> dict:
    """Bo'lim. Yashirilgan bo'lim matnsiz qaytadi — sayt uni chizmaydi.

    `hideable=False` — sayt ishlashi uchun zarur bo'lim (podval, tugmalar):
    u har doim ko'rinadi, admin yashirib qo'ygan bo'lsa ham.
    """
    published = bool(sec.is_published) if hideable else True
    if not published:
        return {"key": sec.key, "page": sec.page, "order": sec.order, "is_published": False, "items": []}
    return {
        "key": sec.key,
        "page": sec.page,
        "order": sec.order,
        "is_published": True,
        "button_url": sec.button_url,
        "button2_url": sec.button2_url,
        "image": media_url(request, sec.image),
        "image2": media_url(request, sec.image2),
        "items": [section_item(request, it, lang) for it in sec.items if it.is_published],
        **translated(sec, SECTION_TR, lang),
    }
