"""Lokal ishlab chiqish muhiti uchun sozlamalar."""

from .base import *  # noqa: F403
from .base import DATABASES, INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

# ---------------------------------------------------------------------------
# Lokal baza — production klasteriga tasodifan yozib qo'ymaslik uchun qo'riq
# ---------------------------------------------------------------------------
# `manage.py` standarti aynan shu fayl. `.env` da esa odatda deploy uchun
# ishlatiladigan `DATABASE_URL` yozib qo'yilgan bo'ladi — ya'ni oddiy
# `python manage.py migrate` PRODUCTION bazasini o'zgartirib yuborishi mumkin.
# Shuning uchun lokal muhitda masofaviy manzil ATAYLAB rad etiladi.
_LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "")
_db_host = str(DATABASES["default"].get("HOST") or "")  # noqa: F405

if _db_host not in _LOCAL_HOSTS:
    if env.bool("ALLOW_REMOTE_DB", default=False):
        import warnings

        warnings.warn(
            f"DIQQAT: lokal muhit MASOFAVIY bazaga ulanmoqda ({_db_host}). "
            "Bu haqiqiy ma'lumotlarni o'zgartiradi.",
            stacklevel=1,
        )
    else:
        # Lokal ishlash uchun jimgina lokal bazaga qaytamiz.
        DATABASES["default"] = env.db_url(  # noqa: F405
            "LOCAL_DATABASE_URL",
            default="postgres://mars_it_school:mars_it_school@localhost:5432/mars_it_school",
        )

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-local-key-not-for-production")

CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)
CSRF_TRUSTED_ORIGINS = env(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:5173", "http://127.0.0.1:5173"],
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Lokalda brute-force bloklash xalaqit bermasligi uchun o'chiriladi.
AXES_ENABLED = False

# Brauzerda API'ni ko'rish qulay bo'lsin.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": "1000/min",
    "user": "1000/min",
    "lead": "100/hour",
    "auth": "100/min",
}

# django-debug-toolbar (o'rnatilgan bo'lsa).
try:
    import debug_toolbar  # noqa: F401
except ImportError:
    pass
else:
    INSTALLED_APPS += ["debug_toolbar"]
    # GZipMiddleware dan keyin turishi kerak (debug_toolbar.W003).
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.middleware.gzip.GZipMiddleware") + 1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = ["127.0.0.1"]
