"""WSGI konfiguratsiyasi (gunicorn shu orqali ishga tushadi)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()

# ---------------------------------------------------------------------------
# Media fayllarni productionda uzatish
# ---------------------------------------------------------------------------
# `config/urls.py` da `/media/` faqat DEBUG=True bo'lganda ochiladi, ya'ni
# productionda admin paneldan yuklangan har bir rasm 404 qaytarardi. Django'ning
# `static()` yordamchisi production uchun mos emas, shuning uchun statik
# fayllarni allaqachon uzatayotgan WhiteNoise'ga media papkasini ham beramiz.
#
# `autorefresh=True` — WhiteNoise odatda fayllar ro'yxatini ishga tushish
# paytida bir marta o'qiydi; media fayllar esa ishlab turgan saytda paydo
# bo'ladi, shuning uchun har so'rovda diskka qaraydi (bu papka kichik).
from django.conf import settings  # noqa: E402
from whitenoise import WhiteNoise  # noqa: E402

# `max_age` — WhiteNoise standart bo'yicha atigi 60 soniya beradi, ya'ni
# brauzer har sahifada barcha rasmlarni qaytadan yuklab olardi (har biri
# Railway'gacha ~0.8 s). Django yuklangan fayl nomiga tasodifiy qo'shimcha
# qo'shadi (`teacher-1_eD5NUKe.webp`), demak nom hech qachon qayta
# ishlatilmaydi — bir yilga keshlash xavfsiz.
MEDIA_MAX_AGE = 60 * 60 * 24 * 365


def add_media_headers(headers, path, url):
    """Media fayllariga xavfsizlik sarlavhalarini qo'shadi.

    WhiteNoise Django ilovasini TASHQARIDAN o'raydi, ya'ni `/media/` so'rovi
    Django middleware zanjiriga umuman kirmaydi. Natijada rasmlar
    `X-Content-Type-Options`, `Content-Security-Policy` va `X-Frame-Options`
    sarlavhalarisiz uzatilardi — API javoblarida esa ularning hammasi bor edi
    (o'lchandi).

    Nima uchun muhim:

    * `nosniff` — brauzer fayl mazmuniga qarab turini "taxmin qilmaydi".
      Nosniff bo'lmasa, `image/*` deb belgilangan, lekin ichida HTML yotgan
      fayl ba'zi brauzerlarda sahifa sifatida bajarilishi mumkin — u ham
      backend domenida, ya'ni admin sessiyasi bilan bir manbada.
    * `Content-Disposition: attachment` + tor CSP — fayl baribir sahifa bo'lib
      ochilsa ham, undagi hech qanday skript ishlamaydi.
    * `X-Frame-Options` — rasm manzilini boshqa saytda `iframe` qilib
      ishlatishning oldini oladi.
    """
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Rasm boshqa saytga resurs sifatida tortilishi mumkin (sayt Vercel'da,
    # rasmlar Railway'da), lekin brauzer imkoniyatlari bu yerda kerak emas.
    headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    # Media — statik resurs; unda hech qachon aktiv mazmun bo'lmasligi kerak.
    headers["Content-Security-Policy"] = (
        "default-src 'none'; img-src 'self'; media-src 'self'; style-src 'none'; "
        "script-src 'none'; sandbox"
    )


if not settings.DEBUG and settings.MEDIA_ROOT:
    application = WhiteNoise(
        application,
        autorefresh=True,
        max_age=MEDIA_MAX_AGE,
        add_headers_function=add_media_headers,
    )
    application.add_files(str(settings.MEDIA_ROOT), prefix=settings.MEDIA_URL)
