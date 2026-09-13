"""Testlar — HAR DOIM alohida lokal baza (`mars_it_school_test`).

Har test funksiyasi oldidan jadvallar tozalanadi. LMS o'chiq: testlar
gamification bazasiga hech qachon tegmaydi.
"""

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://mars_it_school:mars_it_school@localhost:5432/mars_it_school_test",
)

# Sozlamalar `get_settings()` orqali keshlanadi — muhitni importdan OLDIN qo'yamiz.
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["LMS_DATABASE_URL"] = ""
os.environ["PUBLIC_CACHE_SECONDS"] = "0"
import tempfile  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="mars-it-school-test-")
os.environ["MEDIA_ROOT"] = f"{_TMP}/media"
os.environ["PRIVATE_MEDIA_ROOT"] = f"{_TMP}/private"
os.environ["ROOT_PATH"] = ""

from app import db as database  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import site as m  # noqa: E402

get_settings.cache_clear()


async def _ensure_database() -> None:
    """`mars_it_school_test` bo'lmasa yaratamiz (rolda CREATEDB huquqi bor)."""
    admin_url = TEST_DB_URL.rsplit("/", 1)[0] + "/postgres"
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    name = TEST_DB_URL.rsplit("/", 1)[1]
    async with engine.connect() as conn:
        exists = await conn.execute(text("select 1 from pg_database where datname = :n"), {"n": name})
        if exists.scalar() is None:
            await conn.execute(text(f'create database "{name}"'))
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def _schema():
    await _ensure_database()
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.drop_all)
        await conn.run_sync(database.Base.metadata.create_all)
    await engine.dispose()
    yield


@pytest.fixture(autouse=True)
async def _clean_tables():
    """Har testdan oldin barcha jadvallar bo'shatiladi."""
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        names = ", ".join(f'"{t.name}"' for t in reversed(database.Base.metadata.sorted_tables))
        await conn.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    await engine.dispose()
    yield


@pytest.fixture
async def app():
    application = create_app()
    database.init_engines()
    try:
        yield application
    finally:
        await database.dispose_engines()


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def db(app) -> AsyncIterator[AsyncSession]:
    async for session in database.get_db():
        yield session


@pytest.fixture
async def course(db: AsyncSession) -> m.Course:
    direction = m.Direction(slug="programmirovanie", title_ru="Программирование", title_uz="Dasturlash")
    db.add(direction)
    await db.flush()
    c = m.Course(
        slug="it-kids",
        direction_id=direction.id,
        title_ru="IT Kids",
        title_uz="IT Kids (uz)",
        subtitle_ru="Курс для детей",
        description_ru="Описание",
        price=800000,
        age_from=9,
        age_to=11,
    )
    db.add(c)
    await db.flush()
    await db.commit()
    return c
