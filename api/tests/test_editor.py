"""Muharrir: kirish, huquq, bo'limlarni saqlash, rasm yuklash.

Mars ID'ga haqiqiy so'rov yo'q: sessiya cookie'si to'g'ridan-to'g'ri
imzolanadi (`auth.sign`) — xuddi callback muvaffaqiyatli bo'lgandek.
"""

import os

import pytest
from sqlalchemy import select

from app import auth
from app.config import get_settings
from app.models import site as m
from app.services.sections import sync_sections


@pytest.fixture(autouse=True)
def _editor_enabled():
    os.environ["SECRET_KEY"] = "test-editor-secret-0123456789"
    os.environ["MARSID_CLIENT_SECRET"] = "test-client-secret"
    get_settings.cache_clear()
    yield
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("MARSID_CLIENT_SECRET", None)
    get_settings.cache_clear()


def _login(client, role: str = "mentor", is_staff: bool = True):
    """Xodim sessiyasi — callback dan keyingi holat."""
    token = auth.sign({"kind": "session", "sub": "u1", "name": "Xodim", "handle": "xodim", "role": role}, 3600)
    client.cookies.set(get_settings().editor_cookie_name, token)


async def test_login_redirects_to_mars_id_with_signed_state(client):
    r = await client.get("/api/auth/login?next=/kursy", follow_redirects=False)
    assert r.status_code == 302
    loc = r.headers["location"]
    assert loc.startswith("https://id.marshub.uz/oauth/authorize?")
    assert "client_id=school-site" in loc and "state=" in loc
    assert "school_oauth_nonce" in r.headers.get("set-cookie", "")


async def test_login_rejects_open_redirect(client):
    r = await client.get("/api/auth/login?next=https://evil.example", follow_redirects=False)
    state = r.headers["location"].split("state=")[1].split("&")[0]
    from urllib.parse import unquote

    assert auth.verify(unquote(state))["next"] == "/"


async def test_callback_rejects_tampered_state(client):
    r = await client.get("/api/auth/callback?code=x&state=abc.def", follow_redirects=False)
    assert r.status_code == 400


async def test_me_requires_session(client):
    assert (await client.get("/api/auth/me")).status_code == 401
    _login(client)
    r = await client.get("/api/auth/me")
    assert r.status_code == 200 and r.json()["handle"] == "xodim"


async def test_editor_endpoints_require_login(client):
    assert (await client.get("/api/editor/pages")).status_code == 401
    assert (await client.patch("/api/editor/sections/home.hero", json={"values": {}})).status_code == 401


async def test_expired_session_is_rejected(client):
    token = auth.sign({"kind": "session", "sub": "u1", "name": "X", "handle": "x", "role": "admin"}, -1)
    client.cookies.set(get_settings().editor_cookie_name, token)
    assert (await client.get("/api/auth/me")).status_code == 401


async def test_pages_list_all_sections_with_values(client, db):
    await sync_sections(db)
    await db.commit()
    _login(client)
    r = await client.get("/api/editor/pages")
    assert r.status_code == 200
    pages = r.json()
    home = next(p for p in pages if p["key"] == "home")
    hero = next(s for s in home["sections"] if s["key"] == "home.hero")
    assert "title_ru" in hero["values"] and "title_uz" in hero["values"]
    assert hero["fields"] and hero["name"]
    assert "image_url" in hero["values"]


async def test_patch_section_updates_text_bumps_revision_and_clears_cache(client, db):
    await sync_sections(db)
    await db.commit()
    _login(client)

    rev0 = (await client.get("/api/v1/revision/")).json()["revision"]
    r = await client.patch(
        "/api/editor/sections/home.hero",
        json={"values": {"title_ru": "Новый заголовок", "title_uz": "Yangi sarlavha"}},
        headers={"Origin": "http://test"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["values"]["title_ru"] == "Новый заголовок"

    # Ochiq API darhol yangi matnni beradi.
    content = (await client.get("/api/v1/content/?lang=uz")).json()
    assert content["home.hero"]["title"] == "Yangi sarlavha"
    assert (await client.get("/api/v1/revision/")).json()["revision"] > rev0


async def test_patch_rejects_unknown_field_and_foreign_origin(client, db):
    await sync_sections(db)
    await db.commit()
    _login(client)
    r = await client.patch(
        "/api/editor/sections/home.hero", json={"values": {"password": "x"}}, headers={"Origin": "http://test"}
    )
    assert r.status_code == 400
    r = await client.patch(
        "/api/editor/sections/home.hero",
        json={"values": {"title_ru": "x"}},
        headers={"Origin": "https://evil.example"},
    )
    assert r.status_code == 403


async def test_patch_items_replaces_list_in_order(client, db):
    await sync_sections(db)
    await db.commit()
    _login(client)
    # Bo'limni elementlar bilan topamiz.
    pages = (await client.get("/api/editor/pages")).json()
    section = next(s for p in pages for s in p["sections"] if s["item_fields"])
    key = section["key"]
    field = next(f for f in section["item_fields"] if f not in ("icon_name", "icon", "image", "url"))

    r = await client.patch(
        f"/api/editor/sections/{key}",
        json={"items": [{"values": {f"{field}_ru": "Birinchi"}}, {"values": {f"{field}_ru": "Ikkinchi"}}]},
        headers={"Origin": "http://test"},
    )
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    assert [it[f"{field}_ru"] for it in items] == ["Birinchi", "Ikkinchi"]
    assert [it["order"] for it in items] == [0, 1]

    # Bittasini o'chirib, tartibni almashtiramiz.
    second_id = items[1]["id"]
    r = await client.patch(
        f"/api/editor/sections/{key}",
        json={"items": [{"id": second_id, "values": {f"{field}_ru": "Ikkinchi (endi birinchi)"}}]},
        headers={"Origin": "http://test"},
    )
    assert [it["id"] for it in r.json()["items"]] == [second_id]
    section_id = (await db.execute(select(m.PageSection.id).where(m.PageSection.key == key))).scalar_one()
    rows = (await db.execute(select(m.SectionItem).where(m.SectionItem.section_id == section_id))).scalars().all()
    assert [it.id for it in rows] == [second_id]  # o'chirilgani bazadan ham ketgan


async def test_hide_section(client, db):
    await sync_sections(db)
    await db.commit()
    _login(client)
    r = await client.patch(
        "/api/editor/sections/home.hero", json={"is_published": False}, headers={"Origin": "http://test"}
    )
    assert r.json()["is_published"] is False
    assert (await client.get("/api/v1/content/")).json()["home.hero"]["is_published"] is False


async def test_upload_image_validates_content(client):
    _login(client)
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    r = await client.post(
        "/api/editor/upload", files={"file": ("hero.png", png, "image/png")}, headers={"Origin": "http://test"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["path"].startswith("sections/") and r.json()["url"].endswith(".png")
    assert "hero" not in r.json()["path"]  # nom tasodifiy

    fake = await client.post(
        "/api/editor/upload",
        files={"file": ("x.png", b"<svg onload=alert(1)>", "image/png")},
        headers={"Origin": "http://test"},
    )
    assert fake.status_code == 400
    svg = await client.post(
        "/api/editor/upload", files={"file": ("x.svg", b"<svg/>", "image/svg+xml")}, headers={"Origin": "http://test"}
    )
    assert svg.status_code == 400
    traversal = await client.post(
        "/api/editor/upload?folder=../etc",
        files={"file": ("x.png", png, "image/png")},
        headers={"Origin": "http://test"},
    )
    assert traversal.status_code == 400


async def test_logout_clears_cookie(client):
    _login(client)
    r = await client.post("/api/auth/logout", headers={"Origin": "http://test"})
    assert r.status_code == 200
    assert "school_editor=" in r.headers.get("set-cookie", "") and "Max-Age=0" in r.headers.get("set-cookie", "")


def test_redirect_uri_does_not_double_the_prefix():
    """`base_url` proksi ortida `/school` ni o'z ichiga oladi — ikkilanmasin."""
    from types import SimpleNamespace

    from app import auth

    # `/school` prefiksli base_url — mars'dagi holat.
    req = SimpleNamespace(base_url="https://core.marsit.uz/school/")
    assert auth._redirect_uri(req) == "https://core.marsit.uz/school/api/auth/callback"

    # Ildizda (lokal) — prefikssiz.
    req = SimpleNamespace(base_url="http://localhost:8000/")
    assert auth._redirect_uri(req) == "http://localhost:8000/api/auth/callback"
