"""Muharrir — mavjudotlar CRUD va kontaktlar."""

import os

import pytest
from sqlalchemy import select

from app import auth
from app.config import get_settings
from app.models import site as m


@pytest.fixture(autouse=True)
def _editor_enabled():
    os.environ["SECRET_KEY"] = "test-editor-secret-0123456789"
    os.environ["MARSID_CLIENT_SECRET"] = "test-client-secret"
    get_settings.cache_clear()
    yield
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("MARSID_CLIENT_SECRET", None)
    get_settings.cache_clear()


def _login(client):
    token = auth.sign({"kind": "session", "sub": "u1", "name": "X", "handle": "x", "role": "admin"}, 3600)
    client.cookies.set(get_settings().editor_cookie_name, token)


async def test_entities_require_login(client):
    assert (await client.get("/api/editor/entities/branch")).status_code == 401
    assert (await client.get("/api/editor/site-settings")).status_code == 401


async def test_branch_crud_and_public_visibility(client, db):
    _login(client)
    h = {"Origin": "http://test"}

    # создать
    r = await client.post(
        "/api/editor/entities/branch",
        json={
            "values": {"name_ru": "Чиланзар", "name_uz": "Chilonzor", "phone": "+998901112233"},
            "is_published": True,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    branch = r.json()
    assert branch["slug"] == "chilanzar" and branch["name_ru"] == "Чиланзар"

    # виден в публичном API
    pub = (await client.get("/api/v1/branches/?lang=ru")).json()
    assert [b["name"] for b in pub] == ["Чиланзар"]

    # список в редакторе
    lst = (await client.get("/api/editor/entities/branch")).json()
    assert lst["title"] == "Филиалы" and len(lst["items"]) == 1

    # изменить
    r = await client.patch(
        f"/api/editor/entities/branch/{branch['id']}", json={"values": {"name_ru": "Юнусабад"}}, headers=h
    )
    assert r.json()["name_ru"] == "Юнусабад"

    # скрыть → пропадает из публичного
    await client.patch(f"/api/editor/entities/branch/{branch['id']}", json={"is_published": False}, headers=h)
    assert (await client.get("/api/v1/branches/")).json() == []

    # удалить
    r = await client.delete(f"/api/editor/entities/branch/{branch['id']}", headers=h)
    assert r.status_code == 204
    assert (await db.execute(select(m.Branch))).scalar_one_or_none() is None


async def test_slug_is_unique(client, db):
    _login(client)
    h = {"Origin": "http://test"}
    for _ in range(2):
        await client.post("/api/editor/entities/news", json={"values": {"title_ru": "Открытие"}}, headers=h)
    slugs = sorted(n.slug for n in (await db.execute(select(m.News))).scalars())
    assert slugs == ["otkrytie", "otkrytie-2"]


async def test_vacancy_number_and_select(client, db):
    _login(client)
    h = {"Origin": "http://test"}
    r = await client.post(
        "/api/editor/entities/vacancy",
        json={
            "values": {
                "title_ru": "Преподаватель",
                "employment_type": "part_time",
                "salary_from": 5000000,
                "salary_to": "",
            }
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    v = (await db.execute(select(m.Vacancy))).scalar_one()
    assert v.employment_type == "part_time" and v.salary_from == 5000000 and v.salary_to is None


async def test_unknown_field_rejected(client):
    _login(client)
    r = await client.post(
        "/api/editor/entities/branch", json={"values": {"password": "x"}}, headers={"Origin": "http://test"}
    )
    assert r.status_code == 400


async def test_site_settings_edit(client, db):
    _login(client)
    r = await client.get("/api/editor/site-settings")
    assert r.status_code == 200
    assert any(f["name"] == "phone" for f in r.json()["fields"])

    r = await client.patch(
        "/api/editor/site-settings",
        json={"values": {"phone": "+998 78 777 77 57", "telegram_url": "https://t.me/mars"}},
        headers={"Origin": "http://test"},
    )
    assert r.status_code == 200 and r.json()["values"]["phone"] == "+998 78 777 77 57"

    # видно в публичном /site-settings/
    pub = (await client.get("/api/v1/site-settings/")).json()
    assert pub["phone"] == "+998 78 777 77 57" and pub["telegram_url"] == "https://t.me/mars"


async def test_unknown_kind_404(client):
    _login(client)
    assert (await client.get("/api/editor/entities/teachers")).status_code == 404
