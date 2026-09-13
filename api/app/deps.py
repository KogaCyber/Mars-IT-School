"""Umumiy bog'liqliklar: til, mijoz IP, so'rov cheklovi, ochiq javob keshi."""

import time
from collections import OrderedDict
from collections.abc import Callable

from fastapi import HTTPException, Request

from .config import get_settings


def client_ip(request: Request) -> str | None:
    """Proksi ortidagi haqiqiy IP.

    `X-Forwarded-For` ni mijoz o'zi ham yubora oladi, shuning uchun boshidagi
    qiymatga ishonilmaydi: zanjir oxiridan `NUM_PROXIES` qadam orqaga —
    bizning ishonchli proksimiz yozgan manzil. mars: Caddy → nginx = 2.
    """
    proxies = get_settings().num_proxies
    forwarded = request.headers.get("x-forwarded-for", "")
    if proxies and forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            return parts[-min(proxies, len(parts))][:45]
    return request.client.host if request.client else None


# ---------------------------------------------------------------------------
# So'rov cheklovi (xotirada). Ikki worker — ikki hisob; bu maqbul: maqsad
# botni to'xtatish, aniq hisob emas.
# ---------------------------------------------------------------------------

_buckets: dict[str, list[float]] = {}


def rate_limit(scope: str, limit: int, window_seconds: int) -> Callable:
    def dependency(request: Request) -> None:
        key = f"{scope}:{client_ip(request)}"
        now = time.monotonic()
        hits = [t for t in _buckets.get(key, []) if now - t < window_seconds]
        if len(hits) >= limit:
            raise HTTPException(status_code=429, detail="Juda ko'p so'rov. Birozdan keyin urinib ko'ring.")
        hits.append(now)
        _buckets[key] = hits
        # Lug'at cheksiz o'smasin.
        if len(_buckets) > 10_000:
            for k in list(_buckets)[:5_000]:
                _buckets.pop(k, None)

    return dependency


# ---------------------------------------------------------------------------
# Ochiq GET javoblari keshi: kalit = yo'l + oq ro'yxatdagi parametrlar + til
# + kontent versiyasi. Versiya o'zgarsa eski javob o'z-o'zidan yaroqsiz.
# ---------------------------------------------------------------------------

CACHE_PARAMS = frozenset(
    {
        "lang",
        "page",
        "page_size",
        "search",
        "ordering",
        "category__slug",
        "is_featured",
        "direction",
        "age",
        "min_age",
        "max_age",
        "branch",
    }
)


class _TTLCache:
    def __init__(self, capacity: int = 2000):
        self._data: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self.capacity = capacity

    def get(self, key: str):
        item = self._data.get(key)
        if not item:
            return None
        expires, value = item
        if expires < time.monotonic():
            self._data.pop(key, None)
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value, ttl: float) -> None:
        self._data[key] = (time.monotonic() + ttl, value)
        self._data.move_to_end(key)
        while len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def clear(self) -> None:
        self._data.clear()


public_cache = _TTLCache()


def cache_key(request: Request, lang: str, revision: int) -> str:
    params = "&".join(f"{k}={v[:64]}" for k, v in sorted(request.query_params.items()) if k in CACHE_PARAMS)
    return f"{request.url.path}?{params}|{lang}|{revision}"
