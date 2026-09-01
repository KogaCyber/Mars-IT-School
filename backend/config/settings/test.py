"""Testlar uchun sozlamalar — alohida MongoDB bazasi ishlatiladi."""

from .base import *  # noqa: F403
from .base import REST_FRAMEWORK

DEBUG = False
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AXES_ENABLED = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Testlarda so'rov cheklovlari (throttling) o'chiriladi.
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": None,
    "user": None,
    "lead": None,
    "auth": None,
}
