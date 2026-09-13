"""Kontent versiyasi — sayt uni so'rab turadi va o'zgarganda qayta yuklaydi.

Raqam bazada (barcha worker'lar uchun umumiy), 2 soniya xotirada keshlanadi.
Har qanday kontent o'zgarishida (muharrir saqladi) `bump()` chaqiriladi.
"""

import time

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.site import SiteRevision

_cache: tuple[float, int] | None = None
LOCAL_TTL = 2.0


async def current(db: AsyncSession) -> int:
    global _cache
    now = time.monotonic()
    if _cache and now - _cache[0] < LOCAL_TTL:
        return _cache[1]
    value = (await db.execute(select(SiteRevision.value).limit(1))).scalar() or 0
    _cache = (now, int(value))
    return int(value)


async def bump(db: AsyncSession) -> int:
    global _cache
    value = int(time.time() * 1000)
    result = await db.execute(update(SiteRevision).values(value=value))
    if result.rowcount == 0:
        db.add(SiteRevision(value=value))
    await db.flush()
    _cache = (time.monotonic(), value)
    return value
