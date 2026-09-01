"""Production (Railway) muhiti uchun sozlamalar — xavfsizlik maksimal darajada."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env

DEBUG = False

# Railway avtomatik domen beradi; qo'shimcha domenlar ALLOWED_HOSTS orqali.
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
RAILWAY_DOMAIN = env("RAILWAY_PUBLIC_DOMAIN", default="")
if RAILWAY_DOMAIN and RAILWAY_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

# --- HTTPS / transport xavfsizligi -----------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# Railway healthcheck ichki tarmoq orqali HTTP bilan keladi va X-Forwarded-Proto
# qo'ymaydi — HTTPS'ga yo'naltirsak deploy "unhealthy" bo'lib qolardi.
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1 yil
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# --- Cookie'lar -------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 8  # admin sessiyasi 8 soat

# --- Email ------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10

# --- Kesh -------------------------------------------------------------------
# Redis bo'lsa — throttling va axes hisoblari barcha worker'lar uchun umumiy bo'ladi.
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "mars-it-school",
        }
    }

# --- Boshqaruv --------------------------------------------------------------
ADMINS = [("Mars IT School", email) for email in env.list("ADMIN_EMAILS", default=[])]


# --- Sozlamalar to'g'riligini deploy vaqtida tekshirish ---------------------
# Xato konfiguratsiya bilan ishga tushgan sayt jimgina buziladi (CORS, canonical,
# admin manzili). Shuning uchun jarayon boshlanishidayoq to'xtatiladi.
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS bo'sh — production domenini ko'rsating.")

if not CORS_ALLOWED_ORIGINS:  # noqa: F405
    raise ImproperlyConfigured(
        "CORS_ALLOWED_ORIGINS bo'sh — frontend domeni ko'rsatilmasa sayt API'ga ula olmaydi."
    )

if SECRET_KEY in {"change-me", "insecure-local-key-not-for-production"}:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY standart qiymatda qolgan.")

if ADMIN_URL == "admin/" and SERVICE_HAS_ADMIN:  # noqa: F405
    import warnings

    warnings.warn(
        "ADMIN_URL standart '/admin/' da qolgan — uni maxfiy manzilga o'zgartiring.",
        stacklevel=1,
    )
