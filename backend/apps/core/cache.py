"""Ommaviy (autentifikatsiyasiz) API javoblarini keshlash.

Nega kerak: backend Railway'da, MongoDB esa Atlas'da — har bir so'rovga tarmoq
kechikishi qo'shiladi (o'lchandi: bitta so'rov 0.8–1.6 s). Sayt kontenti esa
deyarli o'zgarmaydi. Shuning uchun ochiq GET javoblari:

  1. serverda `cache` ichida saqlanadi — MongoDB'ga qayta murojaat qilinmaydi;
  2. `Cache-Control` bilan brauzer va CDN keshiga beriladi — takroriy tashrifda
     so'rov umuman serverga yetib bormaydi.

Kesh muddati `PUBLIC_CACHE_SECONDS` orqali boshqariladi (0 — keshlash o'chadi).
Admin panelda kontent o'zgarsa esa kutish shart emas: kesh kalitiga kontent
versiyasi qo'shilgan (`revision.py`), shuning uchun o'zgarish bilanoq eski
javob yaroqsiz bo'ladi va sayt yangi ma'lumotni oladi.

**Kesh kaliti va til.** Sayt uch tilda ishlaydi va til `?lang=` yoki
`Accept-Language` orqali keladi. Django'ning tayyor `cache_page` dekoratori
`Vary` sarlavhasiga tayanadi, lekin bu yerda u ishonchli ishlamadi: birinchi
javob (masalan inglizcha) keyingi o'zbekcha so'rovga ham berilib ketardi.
Shuning uchun til kalitning ichiga to'g'ridan-to'g'ri yoziladi — hech qanday
bilvosita mexanizmga tayanmaymiz.
"""

import hashlib
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import patch_cache_control, patch_vary_headers

from .revision import current_revision
from .translation import resolve_language

CACHE_KEY_PREFIX = "publicapi"

#: Sayt so'rovlariga qo'shadigan kontent versiyasi parametri.
VERSION_PARAM = "_v"


def _ttl(explicit=None) -> int:
    if explicit is not None:
        return explicit
    return getattr(settings, "PUBLIC_CACHE_SECONDS", 60)


def _cache_key(request) -> str:
    # `get_full_path()` ichida `?lang=` ham bor, `resolve_language()` esa
    # `Accept-Language` sarlavhasini hisobga oladi — ikkalasi ham kalitda.
    # Kontent versiyasi ham kalitda: admin panelda biror narsa o'zgarishi bilan
    # kalit o'zgaradi va eski javob o'z-o'zidan yaroqsiz bo'ladi.
    raw = f"{request.get_full_path()}|{resolve_language(request)}|{current_revision()}"
    digest = hashlib.md5(raw.encode("utf-8"), usedforsecurity=False).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{digest}"


def _patch_headers(response, ttl: int, request) -> None:
    """Brauzer/CDN uchun keshlash sarlavhalari.

    Sayt har bir so'rovga kontent versiyasini (`_v`) qo'shib yuboradi. Bunday
    manzil kontent o'zgarganda o'zi ham o'zgaradi, shuning uchun javobni
    brauzer va CDN xotirjam keshlashi mumkin — eskirgan nusxa qayta
    so'ralmaydi. `stale-while-revalidate` — muddati tugagan javobni CDN darhol
    beradi va fonda yangilaydi, ya'ni foydalanuvchi kutib turmaydi.

    Versiyasiz so'rov (qidiruv roboti, tashqi mijoz) esa har safar serverdan
    tekshiriladi: aks holda o'zgarish brauzer keshi tufayli bir necha
    daqiqagacha ko'rinmay qolardi. Server javobni o'z xotirasidan beradi,
    shuning uchun bu qimmatga tushmaydi.
    """
    patch_vary_headers(response, ("Accept-Language",))
    if request.GET.get(VERSION_PARAM):
        patch_cache_control(
            response,
            public=True,
            max_age=ttl,
            s_maxage=ttl * 5,
            stale_while_revalidate=ttl * 10,
        )
    else:
        patch_cache_control(response, public=True, max_age=0, must_revalidate=True)


def cached_public_view(view, ttl: int):
    """GET javobini `ttl` soniyaga keshlaydigan o'ram.

    Kesh urilganda view (permission, throttle, serializer, MongoDB) umuman
    ishga tushmaydi — javob tayyor baytlardan qayta yig'iladi.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method not in ("GET", "HEAD"):
            return view(request, *args, **kwargs)

        key = _cache_key(request)
        hit = cache.get(key)
        if hit is not None:
            content, content_type = hit
            response = HttpResponse(content, content_type=content_type)
        else:
            response = view(request, *args, **kwargs)
            # DRF `Response` — "yalqov" javob; keshlash uchun uni shu yerda
            # yakunlaymiz. Undan keyingi middleware'lar (CORS, GZip) baribir
            # tayyor javob ustida ishlaydi.
            if hasattr(response, "render") and not response.is_rendered:
                response.render()
            if response.status_code == 200:
                cache.set(
                    key,
                    (response.content, response.headers.get("Content-Type")),
                    ttl,
                )

        if response.status_code == 200:
            _patch_headers(response, ttl, request)
        return response

    return wrapper


def public_cache(view=None, *, seconds=None):
    """Funksiya-view uchun dekorator."""

    def decorator(func):
        ttl = _ttl(seconds)
        return func if ttl <= 0 else cached_public_view(func, ttl)

    return decorator(view) if view else decorator


class PublicCacheMixin:
    """Ochiq `ReadOnlyModelViewSet`'lar uchun keshlash."""

    cache_seconds = None
    # Qaysi amallar keshlanadi. Yon ta'siri bor amal (masalan yangilikning
    # ko'rishlar sonini oshiradigan `retrieve`) ro'yxatdan chiqariladi.
    cache_actions = ("list", "retrieve")

    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super().as_view(actions, **initkwargs)
        ttl = _ttl(cls.cache_seconds)
        # Router har bir amal uchun alohida view yasaydi, shuning uchun bu yerda
        # aynan shu view qaysi amalga tegishli ekanini bilamiz.
        get_action = (actions or {}).get("get")
        if ttl <= 0 or get_action not in cls.cache_actions:
            return view
        return cached_public_view(view, ttl)
