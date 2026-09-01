"""Lokal ishlab chiqish muhiti uchun sozlamalar."""

from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK, env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]

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
    "apps.core.drf.MongoJSONRenderer",
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
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
