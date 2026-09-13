"""Ikki baza: sayt (yozamiz) va LMS (faqat o'qiymiz)."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """Saytning o'z jadvallari (Alembic shu metadata'dan migratsiya yasaydi)."""


class LmsBase(DeclarativeBase):
    """LMS jadvallari — faqat xaritalash (mapping). Alembic ularga TEGMAYDI."""


_site_engine: AsyncEngine | None = None
_lms_engine: AsyncEngine | None = None
_site_sessions: async_sessionmaker[AsyncSession] | None = None
_lms_sessions: async_sessionmaker[AsyncSession] | None = None


def init_engines() -> None:
    """Lifespan boshida bir marta. Sozlamalar test paytida almashishi mumkin."""
    global _site_engine, _lms_engine, _site_sessions, _lms_sessions
    s = get_settings()
    _site_engine = create_async_engine(s.database_url, pool_size=5, max_overflow=5, pool_pre_ping=True)
    _site_sessions = async_sessionmaker(_site_engine, expire_on_commit=False)
    if s.lms_enabled:
        # LMS bazasi boshqa loyihaniki: ozgina ulanish, hammasi READ ONLY.
        _lms_engine = create_async_engine(
            s.lms_database_url,
            pool_size=2,
            max_overflow=2,
            pool_pre_ping=True,
            execution_options={"postgresql_readonly": True},
        )
        _lms_sessions = async_sessionmaker(_lms_engine, expire_on_commit=False)


async def dispose_engines() -> None:
    global _site_engine, _lms_engine
    if _site_engine is not None:
        await _site_engine.dispose()
    if _lms_engine is not None:
        await _lms_engine.dispose()
    _site_engine = _lms_engine = None


def site_engine() -> AsyncEngine:
    assert _site_engine is not None, "init_engines() chaqirilmagan"
    return _site_engine


async def get_db() -> AsyncIterator[AsyncSession]:
    """Sayt bazasi. Har so'rov — bitta sessiya, xato bo'lsa rollback."""
    assert _site_sessions is not None, "init_engines() chaqirilmagan"
    async with _site_sessions() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_lms() -> AsyncIterator[AsyncSession | None]:
    """LMS bazasi (faqat o'qish). LMS o'chirilgan bo'lsa `None` — kod buni kutadi."""
    if _lms_sessions is None:
        yield None
        return
    async with _lms_sessions() as session:
        yield session
