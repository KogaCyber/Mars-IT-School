"""Ochiq API: shakl, til, kesh, sahifalash."""

from sqlalchemy import select

from app.models import site as m
from app.services import revision
from app.services.sections import SECTIONS, sync_sections

LIST_ENDPOINTS = [
    "/api/v1/courses/",
    "/api/v1/directions/",
    "/api/v1/teachers/",
    "/api/v1/branches/",
    "/api/v1/news-categories/",
    "/api/v1/vacancies/",
    "/api/v1/quizzes/",
    "/api/v1/advantages/",
    "/api/v1/reviews/",
    "/api/v1/faqs/",
    "/api/v1/space-features/",
    "/api/v1/statistics/",
    "/api/v1/founders/",
    "/api/v1/future-benefits/",
    "/api/v1/child-skills/",
    "/api/v1/project-defence-steps/",
    "/api/v1/school-features/",
]


async def test_health(client):
    r = await client.get("/health/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": True}


async def test_every_list_endpoint_answers_with_a_list(client):
    for path in LIST_ENDPOINTS:
        r = await client.get(path)
        assert r.status_code == 200, path
        assert r.json() == [], path


async def test_news_is_paginated_like_drf(client):
    r = await client.get("/api/v1/news/")
    assert r.json() == {"count": 0, "next": None, "previous": None, "results": []}


async def test_home_bootstrap_shape(client):
    r = await client.get("/api/v1/home/")
    assert r.status_code == 200
    assert set(r.json()) == {"settings", "sections", "advantages", "reviews", "faqs", "teachers", "news"}


async def test_course_list_and_detail_shape(client, course):
    r = await client.get("/api/v1/courses/")
    (item,) = r.json()
    assert item["id"] == course.id and isinstance(item["id"], int)
    assert item["slug"] == "it-kids"
    assert item["age_range"] == "9–11"
    assert item["price"] == "800000"  # DecimalField Django'da satr edi — sayt shuni kutadi
    assert item["direction"] == "programmirovanie"
    assert item["title"] == "IT Kids"

    r = await client.get("/api/v1/courses/it-kids/")
    detail = r.json()
    for key in ("description", "hero_image", "lesson_duration_minutes", "teachers", "features", "stages", "faqs"):
        assert key in detail, key


async def test_language_switch(client, course):
    ru = (await client.get("/api/v1/courses/?lang=ru")).json()[0]
    uz = (await client.get("/api/v1/courses/?lang=uz")).json()[0]
    en = (await client.get("/api/v1/courses/", headers={"Accept-Language": "en-US,en;q=0.9"})).json()[0]
    assert ru["title"] == "IT Kids"
    assert uz["title"] == "IT Kids (uz)"
    # Inglizcha tarjima bo'sh — asosiy tilga (ru) qaytadi.
    assert en["title"] == "IT Kids"


async def test_unpublished_course_is_hidden(client, db, course):
    course.is_published = False
    await db.commit()
    assert (await client.get("/api/v1/courses/")).json() == []
    assert (await client.get("/api/v1/courses/it-kids/")).status_code == 404


async def test_course_filters(client, db, course):
    db.add(m.Course(slug="teens", title_ru="Teens", description_ru="x", age_from=12, age_to=17, price=1))
    await db.commit()
    assert len((await client.get("/api/v1/courses/")).json()) == 2
    assert [c["slug"] for c in (await client.get("/api/v1/courses/?age=10")).json()] == ["it-kids"]
    assert [c["slug"] for c in (await client.get("/api/v1/courses/?direction=programmirovanie")).json()] == ["it-kids"]
    assert [c["slug"] for c in (await client.get("/api/v1/courses/?search=Teens")).json()] == ["teens"]


async def test_sections_sync_and_content(client, db):
    result = await sync_sections(db)
    await db.commit()
    assert result["created"] == len(SECTIONS)
    # Ikkinchi marta — hech narsa yaratilmaydi, mavjud matn saqlanadi.
    assert (await sync_sections(db))["created"] == 0

    content = (await client.get("/api/v1/content/?lang=ru")).json()
    assert len(content) == len(SECTIONS)
    hero = content["home.hero"]
    assert hero["is_published"] is True
    assert hero["title"]  # standart matn bilan to'ldirilgan


async def test_hidden_section_returns_stub(client, db):
    await sync_sections(db)
    hero = (await db.execute(select(m.PageSection).where(m.PageSection.key == "home.hero"))).scalar_one()
    hero.is_published = False
    await db.commit()
    data = (await client.get("/api/v1/content/")).json()["home.hero"]
    assert data["is_published"] is False
    assert "title" not in data  # yashirilgan bo'lim matnsiz


async def test_news_pagination_and_view_counter(client, db):
    for i in range(15):
        db.add(m.News(slug=f"n{i}", title_ru=f"Yangilik {i}", excerpt_ru="", body_ru="matn"))
    await db.commit()

    page1 = (await client.get("/api/v1/news/?page_size=10")).json()
    assert page1["count"] == 15 and len(page1["results"]) == 10
    assert page1["next"] and "page=2" in page1["next"]
    assert page1["previous"] is None
    page2 = (await client.get("/api/v1/news/?page_size=10&page=2")).json()
    assert len(page2["results"]) == 5 and page2["next"] is None

    first = (await client.get("/api/v1/news/n0/")).json()
    second = (await client.get("/api/v1/news/n0/")).json()
    assert second["views_count"] == first["views_count"] + 1
    assert "body" in second and "gallery" in second


async def test_revision_endpoint_is_not_cached(client, db):
    r0 = (await client.get("/api/v1/revision/")).json()["revision"]
    await revision.bump(db)
    await db.commit()
    r1 = (await client.get("/api/v1/revision/")).json()["revision"]
    assert r1 > r0


async def test_validation_error_shape_matches_old_api(client):
    r = await client.post("/api/v1/leads/", json={"full_name": "A B", "phone": "123"})
    assert r.status_code == 400
    body = r.json()
    assert body["detail"] and "phone" in body["errors"]
