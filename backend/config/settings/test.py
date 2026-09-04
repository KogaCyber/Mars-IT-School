"""Testlar uchun sozlamalar — HAR DOIM lokal MongoDB ishlatiladi."""

from .base import *  # noqa: F403
from .base import BASE_DIR, DATABASES, REST_FRAMEWORK, env

DEBUG = False
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Ma'lumotlar bazasi — ATAYLAB `.env` dan olinmaydi
# ---------------------------------------------------------------------------
# Ilgari bu yerda hech narsa qayta belgilanmasdi va testlar `.env` dagi
# `MONGODB_URI` ni, ya'ni PRODUCTION Atlas klasterini ishlatardi. Oqibatlari:
#
#   * har bir amal Yevropa ↔ Singapur oralig'ini bosib o'tardi — 30 ta test
#     10 daqiqa 19 soniya davom etardi (o'lchangan);
#   * ikki kishi (yoki CI va ishlab chiquvchi) bir vaqtda test yurgizsa bitta
#     masofaviy bazani talashib, bir-birining kolleksiyalarini buzardi;
#   * ishlab chiqish mashinasidan production infratuzilmasiga yozish yo'li
#     ochiq turardi.
#
# Testlar hech qachon masofaviy bazaga tegmasligi kerak. Kerak bo'lsa
# `TEST_MONGODB_URI` orqali boshqa LOKAL manzil beriladi.
DATABASES["default"]["HOST"] = env("TEST_MONGODB_URI", default="mongodb://localhost:27017")
DATABASES["default"]["NAME"] = "mars_it_school_test"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AXES_ENABLED = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Testlarda vaqtinchalik papkalar — haqiqiy media/ ga tegilmaydi.
MEDIA_ROOT = BASE_DIR / ".test-media"
PRIVATE_MEDIA_ROOT = BASE_DIR / ".test-private-media"

# Ro'yxatdan o'tish testlari uchun yoqiladi (productionda standart — o'chiq).
PUBLIC_REGISTRATION_ENABLED = True

# Keshlash testlarni bir-biriga bog'lab qo'ymasligi kerak.
PUBLIC_CACHE_SECONDS = 0
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Testlarda so'rov cheklovlari (throttling) o'chiriladi.
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = dict.fromkeys(
    ("anon", "user", "lead", "auth", "revision", "health")
)
