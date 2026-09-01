"""Filial koordinatalarini aniqlash.

Xaritadagi nishon `latitude`/`longitude` bo'yicha chiziladi — manzil matni
o'zgargani bilan nishon o'z-o'zidan siljimaydi. Shu modul admin panelda
saqlash paytida koordinatani ikki yo'l bilan yangilaydi:

1. Yandex/Google havolasidan ajratib olish — tarmoqqa chiqmaydi, aniq.
2. Manzil bo'yicha geokodlash (OpenStreetMap Nominatim) — havolada koordinata
   bo'lmasa ishlatiladi.

Ikkalasi ham "best effort": xatolik saqlashni to'xtatmaydi, faqat admin
panelda ogohlantirish ko'rsatiladi.
"""

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

USER_AGENT = "MarsITSchool-Admin/1.0 (+https://marsit.uz)"
TIMEOUT = 6

# SSRF'ning oldini olish uchun faqat shu domenlarga murojaat qilinadi.
ALLOWED_MAP_HOSTS = (
    "google.com",
    "google.co.uz",
    "goo.gl",
    "yandex.ru",
    "yandex.uz",
    "yandex.com",
    "ya.ru",
)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Google havolasida ikki xil koordinata bo'ladi:
#   !3d..!4d.. — obyektning o'zi (aniq nuqta),
#   @..,..     — kamera markazi (obyektdan 100-300 metr chetda bo'lishi mumkin).
# Shuning uchun avval !3d/!4d qidiriladi.
_GOOGLE_PLACE = re.compile(r"!3d(-?\d{1,3}\.\d+)!4d(-?\d{1,3}\.\d+)")
_GOOGLE_CAMERA = re.compile(r"@(-?\d{1,3}\.\d+),(-?\d{1,3}\.\d+)")
# Ikkita son: "41.311081,69.240562" (query parametrlari ichidan)
_PAIR = re.compile(r"^(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)")


def _host(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")


def _allowed(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = _host(url)
    return any(host == domain or host.endswith(f".{domain}") for domain in ALLOWED_MAP_HOSTS)


def _valid(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0.0, 0.0)


def _pair_from(value: str) -> tuple[float, float] | None:
    match = _PAIR.match(value.strip())
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def _expand_short_url(url: str) -> str:
    """Qisqa havolani (maps.app.goo.gl, yandex.ru/maps/-/…) to'liq manzilga yozadi."""
    try:
        # Manzil ALLOWED_MAP_HOSTS bilan cheklangan (yuqorida tekshiriladi).
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            return response.geturl()
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        logger.info("Qisqa xarita havolasi ochilmadi: %s", url)
        return url


def coords_from_map_url(url: str) -> tuple[float, float] | None:
    """Yandex yoki Google havolasidan (kenglik, uzunlik) ajratadi.

    Yandex koordinatani `uzunlik,kenglik` tartibida, Google esa
    `kenglik,uzunlik` tartibida yozadi — shuning uchun domen tekshiriladi.
    """
    url = (url or "").strip()
    if not url or not _allowed(url):
        return None

    # Qisqa havolada koordinata bo'lmaydi — avval to'liq manzilga yoziladi.
    if _host(url) in ("goo.gl", "maps.app.goo.gl", "ya.ru") or "/maps/-/" in url:
        url = _expand_short_url(url)

    is_yandex = "yandex" in _host(url) or "ya.ru" in _host(url)

    if not is_yandex:
        for pattern in (_GOOGLE_PLACE, _GOOGLE_CAMERA):
            match = pattern.search(url)
            if match:
                lat, lon = float(match.group(1)), float(match.group(2))
                if _valid(lat, lon):
                    return lat, lon

    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    # Yandex: ll / pt / whatshere[point] — hammasi «uzunlik,kenglik».
    # Google: q / query / ll / center — hammasi «kenglik,uzunlik».
    keys = ("ll", "pt", "whatshere[point]") if is_yandex else ("q", "query", "ll", "center")
    for key in keys:
        for raw in query.get(key, []):
            pair = _pair_from(raw)
            if not pair:
                continue
            lat, lon = (pair[1], pair[0]) if is_yandex else pair
            if _valid(lat, lon):
                return lat, lon

    return None


def geocode_address(address: str) -> tuple[float, float, str] | None:
    """Manzil matnidan koordinata topadi (OpenStreetMap Nominatim).

    Qaytaradi: (kenglik, uzunlik, topilgan joy nomi). Nominatim O'zbekiston
    manzillarini har doim ham aniq topa olmaydi — shuning uchun topilgan joy
    nomi ham qaytariladi va admin panelda ko'rsatiladi (tekshirish uchun).
    """
    address = (address or "").strip()
    if not address:
        return None

    params = urllib.parse.urlencode(
        {
            "q": address,
            "format": "json",
            "limit": 1,
            "accept-language": "ru",
            "countrycodes": "uz",
        }
    )
    # Manzil doimiy (nominatim.openstreetmap.org) — foydalanuvchi kiritmaydi.
    request = urllib.request.Request(  # noqa: S310
        f"{NOMINATIM_URL}?{params}", headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            results = json.loads(response.read().decode())
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        logger.info("Geokodlash amalga oshmadi: %s", address)
        return None

    if not results:
        return None

    try:
        lat, lon = float(results[0]["lat"]), float(results[0]["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    label = str(results[0].get("display_name", ""))[:120]
    return (lat, lon, label) if _valid(lat, lon) else None


def resolve_coordinates(branch, changed_fields: set[str]) -> tuple[bool, str]:
    """Filial koordinatasini yangilaydi.

    Qaytaradi: (ishonchli manbadan olindimi, admin panelda ko'rsatiladigan xabar).
    Birinchi qiymat `False` bo'lsa, xabar ogohlantirish sifatida chiqadi —
    koordinata umuman o'zgarmagan yoki taxminiy (geokodlash) bo'lishi mumkin.

    Tartib:
      1. Koordinata qo'lda tahrirlangan bo'lsa — tegilmaydi.
      2. Xarita havolasidan ajratib olinadi (aniq).
      3. Bo'lmasa — manzil bo'yicha geokodlanadi (taxminiy, tekshirish kerak).
    """
    if {"latitude", "longitude"} & changed_fields:
        return False, ""

    has_coords = branch.latitude is not None and branch.longitude is not None
    triggers = {"address_ru", "landmark_ru", "map_url_yandex", "map_url_google"} & changed_fields
    if has_coords and not triggers:
        return False, ""

    for field in ("map_url_google", "map_url_yandex"):
        coords = coords_from_map_url(getattr(branch, field, ""))
        if not coords:
            continue
        if (branch.latitude, branch.longitude) == coords:
            return False, ""
        branch.latitude, branch.longitude = coords
        label = "Google Maps" if field == "map_url_google" else "Yandex Maps"
        return True, (
            f"Xaritadagi nishon ko'chirildi — koordinata {label} havolasidan olindi: "
            f"{coords[0]}, {coords[1]}."
        )

    address = branch.address_ru
    if branch.landmark_ru:
        address = f"{address}, {branch.landmark_ru}"

    found = geocode_address(address)
    if found:
        lat, lon, place = found
        if (branch.latitude, branch.longitude) == (lat, lon):
            return False, ""
        branch.latitude, branch.longitude = lat, lon
        return False, (
            f"Koordinata manzil bo'yicha taxminan topildi: {lat}, {lon} — «{place}». "
            "Xaritada tekshiring! Noto'g'ri bo'lsa, Yandex yoki Google havolasini "
            "qo'ying — havoladan olingan koordinata aniq bo'ladi."
        )

    if not has_coords:
        return False, (
            "Koordinata topilmadi — filial xaritada ko'rinmaydi. "
            "Yandex yoki Google havolasini qo'ying, yoki kenglik/uzunlikni qo'lda kiriting."
        )

    return False, (
        "Manzil o'zgardi, lekin koordinata topilmadi — xaritadagi nishon eski joyida qoldi. "
        "Xarita havolasini yangilang yoki kenglik/uzunlikni qo'lda to'g'rilang."
    )
