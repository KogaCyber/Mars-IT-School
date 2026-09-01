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

if not settings.DEBUG and settings.MEDIA_ROOT:
    application = WhiteNoise(application, autorefresh=True, max_age=MEDIA_MAX_AGE)
    application.add_files(str(settings.MEDIA_ROOT), prefix=settings.MEDIA_URL)
