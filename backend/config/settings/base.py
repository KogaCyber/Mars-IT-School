"""
Umumiy (barcha muhitlar uchun) Django sozlamalari.

Muhitga bog'liq qiymatlar `local.py` va `production.py` da qayta belgilanadi.
Hech qanday maxfiy qiymat (secret) shu faylga yozilmaydi — faqat .env orqali.
"""

import ipaddress
from datetime import timedelta
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

# ---------------------------------------------------------------------------
# Yo'llar (paths)
# ---------------------------------------------------------------------------
# base.py -> settings/ -> config/ -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# .env fayli mavjud bo'lsa o'qiladi (productionda odatda real env o'zgaruvchilar).
env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(str(env_file))

# ---------------------------------------------------------------------------
# Xavfsizlik (asosiy)
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Xizmat roli — qaysi URL'lar ochilishini belgilaydi
# ---------------------------------------------------------------------------
# Admin panel va ommaviy API alohida portlarda (alohida jarayonlarda) ishlashi
# uchun. Kod bazasi bitta, lekin har bir jarayon faqat o'z URL'larini ochadi:
#   api   — faqat /api/v1/ va /health/ (admin panel bu portda umuman yo'q)
#   admin — faqat admin panel va /health/
#   all   — hammasi bitta portda (eski xatti-harakat, standart qiymat)
SERVICE_ROLE = env("SERVICE_ROLE", default="all")
if SERVICE_ROLE not in {"api", "admin", "all"}:
    raise ImproperlyConfigured(
        f"SERVICE_ROLE noto'g'ri: {SERVICE_ROLE!r}. Ruxsat etilgan: api, admin, all."
    )

SERVICE_HAS_API = SERVICE_ROLE in {"api", "all"}
SERVICE_HAS_ADMIN = SERVICE_ROLE in {"admin", "all"}

# Admin panel manzili (productionda maxfiy qiymatga o'zgartiriladi).
ADMIN_URL = env("ADMIN_URL", default="admin/")
if not ADMIN_URL.endswith("/"):
    ADMIN_URL += "/"

# Admin panelga kirish ruxsat etilgan IP manzillar yoki tarmoqlar
# (masalan: "84.54.72.10,84.54.73.0/24"). Bo'sh bo'lsa — cheklov yo'q.
# To'ldirilsa, parol o'g'irlangan taqdirda ham hujumchi admin paneliga
# umuman yeta olmaydi (`apps/core/middleware.py`).
ADMIN_ALLOWED_IPS = env.list("ADMIN_ALLOWED_IPS", default=[])
for _network in ADMIN_ALLOWED_IPS:
    try:
        ipaddress.ip_network(_network.strip(), strict=False)
    except ValueError as _exc:
        raise ImproperlyConfigured(
            f"ADMIN_ALLOWED_IPS ichida noto'g'ri manzil: {_network!r}"
        ) from _exc

# ---------------------------------------------------------------------------
# Ilovalar
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    # MongoDB uchun moslashtirilgan konfiguratsiyalar (config/mongo_apps.py).
    "config.mongo_apps.MongoAdminConfig",
    "config.mongo_apps.MongoAuthConfig",
    "config.mongo_apps.MongoContentTypesConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "config.mongo_apps.MongoAxesConfig",
]

LOCAL_APPS = [
    "apps.core",  # sayt sozlamalari, FAQ, afzalliklar, ota-onalar fikri
    "apps.accounts",  # foydalanuvchilar va autentifikatsiya
    "apps.courses",  # kurslar va o'qish bosqichlari
    "apps.teachers",  # o'qituvchilar
    "apps.news",  # yangiliklar va galereya
    "apps.branches",  # filiallar va xarita
    "apps.vacancies",  # vakansiyalar va ularga arizalar
    "apps.quiz",  # proforientatsiya testi va natijalar
    "apps.leads",  # saytdagi arizalar
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware (tartib muhim!)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Django qo'ymaydigan sarlavhalar (Permissions-Policy, CORP) va
    # `Server` sarlavhasini olib tashlash. Eng tashqarida turadi — shunda
    # ichkaridagi HAR QANDAY javob (xatoliklar ham) sarlavhalarni oladi.
    "apps.core.middleware.SecurityHeadersMiddleware",
    # GZip — API javoblari va admin HTML simda ~4 barobar kichrayadi.
    "django.middleware.gzip.GZipMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Til tanlash: admin panel tilini seansda saqlaydi (Ruscha / O'zbekcha).
    # Tartib muhim — SessionMiddleware'dan keyin, CommonMiddleware'dan oldin.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Autentifikatsiyadan KEYIN: admin panelga kirish urinishini qayd etishda
    # foydalanuvchi ma'lum bo'lishi kerak.
    "apps.core.middleware.AdminAccessMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    # django-axes eng oxirida: autentifikatsiya natijasini kuzatadi.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Admin bo'limi saytning qayerini o'zgartirishi haqidagi eslatma.
                "apps.core.context_processors.admin_section_help",
                # Admin paneldagi til almashtirgichi (Ruscha / O'zbekcha).
                "apps.core.context_processors.admin_languages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Ma'lumotlar bazasi
# ---------------------------------------------------------------------------
# MongoDB (django-mongodb-backend). Ulanish satri MONGODB_URI orqali beriladi:
#   lokal:      mongodb://localhost:27017/mars_it_school
#   Atlas/Railway: mongodb+srv://user:pass@cluster/mars_it_school?retryWrites=true&w=majority
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": env("MONGODB_URI", default="mongodb://localhost:27017"),
        "NAME": env("MONGODB_NAME", default="mars_it_school"),
    }
}

# MongoDB tranzaksiyalarni Django ORM darajasida qo'llab-quvvatlamaydi,
# shuning uchun ATOMIC_REQUESTS ishlatilmaydi (yozish amallari idempotent yozilgan).
DATABASES["default"]["ATOMIC_REQUESTS"] = False

# Embedded (ichki) modellar alohida kolleksiya yaratmasligi uchun router kerak.
DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter"]

# Mongo hujjatlarining birlamchi kaliti — ObjectId.
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

# Django/uchinchi tomon ilovalarining tayyor migratsiyalari AutoField ishlatadi,
# shuning uchun ular Mongo uchun qaytadan yaratiladi (mongo_migrations/ papkasi).
MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
    "axes": "mongo_migrations.axes",
}

# ---------------------------------------------------------------------------
# Autentifikatsiya
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend birinchi bo'lishi shart (brute-force himoyasi).
    "axes.backends.AxesStandaloneBackend",
    "apps.accounts.backends.EmailOrPhoneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Argon2 — Django tavsiya qiladigan eng kuchli parol hasher.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- django-axes: login urinishlarini cheklash ------------------------------
AXES_FAILURE_LIMIT = env.int("AXES_FAILURE_LIMIT", default=5)
AXES_COOLOFF_TIME = timedelta(minutes=env.int("AXES_COOLOFF_MINUTES", default=30))
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ADMIN = True
AXES_LOCKOUT_TEMPLATE = None
# Proksi orqasida REMOTE_ADDR — bu proksining IP'si. Uni ishlatsak bitta
# foydalanuvchining xato paroli hammani bloklab qo'yardi. Shuning uchun
# X-Forwarded-For zanjiridan oxirgi (proksi qo'ygan, ishonchli) manzil olinadi.
AXES_IPWARE_PROXY_COUNT = env.int("NUM_PROXIES", default=1) or None
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"]

# ---------------------------------------------------------------------------
# Xalqarolashtirish
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "ru"
LANGUAGES = [
    ("ru", "Русский"),
    ("uz", "O'zbekcha"),
    ("en", "English"),
]
# Kontent tarjimalari uchun ishlatiladigan tillar (model maydonlari: _ru/_uz/_en).
CONTENT_LANGUAGES = ["ru", "uz", "en"]
DEFAULT_CONTENT_LANGUAGE = "ru"
# Birinchi papkaga `makemessages` yozadi (loyihaning o'z satrlari).
# Ikkinchisi qo'lda yuritiladi: Django'ning o'zbekcha admin tarjimasidagi
# bo'shliqlarni to'ldiradi (u yerda satrlarning yarmi tarjimasiz va ular
# `LANGUAGE_CODE` = ru katalogiga qaytib, ruscha chiqib qolardi).
LOCALE_PATHS = [BASE_DIR / "locale", BASE_DIR / "locale_overrides"]
# Admin panel interfeysi shu tillarda almashadi (sayt kontenti — CONTENT_LANGUAGES).
ADMIN_LANGUAGES = ["ru", "uz"]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Statik va media fayllar
# ---------------------------------------------------------------------------
# Nomida hash bo'lgan fayllarni (ManifestStaticFilesStorage) WhiteNoise o'zi
# `immutable`, bir yillik kesh bilan beradi. Bu qiymat esa hashsiz fayllarga
# tegishli — standart 60 soniya juda qisqa, lekin bir yil ham xavfli, shuning
# uchun bir kun.
WHITENOISE_MAX_AGE = 60 * 60 * 24

# --- Sayt yo'l prefiksi (sub-path) ------------------------------------------
# Ilova domen ildizida emas, boshqa saytning ichki yo'lida ham turishi mumkin
# (masalan `core.marsit.uz/school/`). Bunda proksi to'liq manzilni o'zgarishsiz
# uzatadi, Django esa o'zi yasagan HAR BIR manzilga (admin panel havolalari,
# `redirect()`, statik va media fayllar) shu prefiksni qo'shishi kerak — aks
# holda admin paneldagi har bir havola prefikssiz chiqib, 404 berardi.
#
# Bo'sh bo'lsa hech narsa o'zgarmaydi: sayt avvalgidek ildizda ishlaydi.
FORCE_SCRIPT_NAME = env("FORCE_SCRIPT_NAME", default="").rstrip("/") or None

#: Statik va media manzillari uchun prefiks (`FORCE_SCRIPT_NAME` ularga
#: avtomatik qo'shilmaydi — Django ularni faqat `STATIC_URL` dan oladi).
_URL_PREFIX = FORCE_SCRIPT_NAME or ""

STATIC_URL = f"{_URL_PREFIX}/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = f"{_URL_PREFIX}/media/"
# Railway'da konteyner disk vaqtinchalik: har deploy'da yuklangan rasmlar
# yo'qoladi. Shuning uchun MEDIA_ROOT doimiy volume'ga yo'naltiriladi
# (Railway → Volumes → mount path, masalan /data/media).
MEDIA_ROOT = Path(env("MEDIA_ROOT", default=str(BASE_DIR / "media")))

# --- Shaxsiy (himoyalangan) fayllar ----------------------------------------
# `MEDIA_ROOT` ni WhiteNoise butunlay ochiq uzatadi (config/wsgi.py), ya'ni u
# yerdagi har bir fayl manzilini bilgan odamga ko'rinadi. Nomzodlarning
# rezyumesi esa shaxsiy ma'lumot. Shuning uchun u ALOHIDA, hech qachon
# statik uzatilmaydigan papkada saqlanadi va faqat
# `apps/vacancies/views.py:resume_download_view` orqali, xodim huquqi bilan
# beriladi. Bu papka MEDIA_ROOT ichida BO'LMASLIGI shart.
# `.env` da kalit bor-u qiymati bo'sh bo'lishi mumkin — bu ko'p uchraydigan
# holat. `Path("")` esa joriy ishchi papkaga (`.`) aylanadi, ya'ni rezyumelar
# tasodifiy joyga yozilardi. Shuning uchun bo'sh qiymat "berilmagan" deb
# hisoblanadi va `resolve()` bilan har doim absolut yo'lga keltiriladi.
PRIVATE_MEDIA_ROOT = Path(
    env("PRIVATE_MEDIA_ROOT", default="").strip() or str(BASE_DIR / "private-media")
).resolve()

_media_root_resolved = MEDIA_ROOT.resolve()
if (
    _media_root_resolved == PRIVATE_MEDIA_ROOT
    or _media_root_resolved in PRIVATE_MEDIA_ROOT.parents
    or PRIVATE_MEDIA_ROOT in _media_root_resolved.parents
):
    raise ImproperlyConfigured(
        f"PRIVATE_MEDIA_ROOT ({PRIVATE_MEDIA_ROOT}) va MEDIA_ROOT "
        f"({_media_root_resolved}) biri ikkinchisining ichida bo'lmasligi kerak — "
        "aks holda rezyume fayllari WhiteNoise orqali ommaga ochiq bo'lib qoladi."
    )

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Yuklanadigan fayl hajmi cheklovi (5 MB) — DoS va disk to'lib qolishiga qarshi.
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 500

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Standart sinf emas: bu sinf tokendagi `epoch` da'vosini ham
        # tekshiradi, ya'ni parol o'zgarganda eski tokenlar darhol yaroqsiz
        # bo'ladi (apps/accounts/authentication.py).
        "apps.accounts.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("apps.core.drf.MongoJSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "apps.core.filters.SafeSearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "240/min",
        # Ariza yuborish. O'zbekistonda mobil operatorlar va maktab/ofis
        # tarmoqlari CGNAT ishlatadi — bitta IP ortida yuzlab odam turadi.
        # 5/hour bunday tarmoqdagi haqiqiy mijozni bloklab qo'yardi.
        # Spamga qarshi asosiy himoya honeypot va telefon validatsiyasi.
        "lead": env("LEAD_THROTTLE_RATE", default="40/hour"),
        "auth": "10/min",  # login / register
        # Test natijasi havolasi. Kalit taxmin qilib bo'lmaydigan bo'lsa ham,
        # cheklov sanash urinishini (enumeration) butunlay ma'nosiz qiladi.
        "result": "30/min",
        # Kontent versiyasi: sayt uni har 5 soniyada so'raydi (12/min), javob
        # server xotirasidan keladi. Limit shunchaki cheksiz so'rovni to'xtatadi.
        "revision": "120/min",
        # Railway healthcheck va monitoring — ular umumiy `anon` limitini
        # to'ldirib, haqiqiy tashrifchilarni siqib chiqarmasligi kerak.
        "health": "120/min",
    },
    # Proksi (Railway/Vercel) orqasida throttling kimni cheklashini aniqlash uchun.
    # `None` bo'lganda DRF butun X-Forwarded-For zanjirini kalit sifatida oladi —
    # sarlavhani soxtalashtirib har safar yangi "hisob" ochish va cheklovni
    # aylanib o'tish mumkin bo'ladi. Ishonchli proksi soni aniq beriladi.
    "NUM_PROXIES": env.int("NUM_PROXIES", default=1),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
    "DEFAULT_VERSIONING_CLASS": None,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", default=15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    # Blacklist o'rniga o'zimizning `RevokedRefreshToken` modeli ishlatiladi
    # (simplejwt'ning blacklist ilovasi MongoDB bilan mos kelmaydi).
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "apps.accounts.serializers.TokenObtainSerializer",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Mars IT School API",
    "DESCRIPTION": "Mars IT School rasmiy sayti uchun REST API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    # `icon_name` maydoni uchta modelda bor va har birida BOSHQA ro'yxat.
    # Generator ularni "IconNameDdeEnum" kabi tushunarsiz nom bilan ajratardi —
    # bu yerda har biriga aniq nom beriladi.
    "ENUM_NAME_OVERRIDES": {
        "VacancyIconEnum": "apps.vacancies.models.Vacancy.Icon",
        "ChildSkillIconEnum": "apps.core.models.ChildSkill.Icon",
        "ProjectDefenceStepIconEnum": "apps.core.models.ProjectDefenceStep.Icon",
    },
}

# Ilova oldida turgan ishonchli proksilar soni (Railway/Vercel = 1).
# Proksisiz (to'g'ridan-to'g'ri) ishlatilsa 0 qilinadi.
NUM_PROXIES = env.int("NUM_PROXIES", default=1)

# ---------------------------------------------------------------------------
# Kesh
# ---------------------------------------------------------------------------
# Ochiq (autentifikatsiyasiz) API javoblari shuncha soniya keshlanadi —
# apps/core/cache.py ga qarang. 0 qilinsa keshlash butunlay o'chadi.
PUBLIC_CACHE_SECONDS = env.int("PUBLIC_CACHE_SECONDS", default=60)

# Admin sessiyasi har so'rovda MongoDB'dan o'qilmasligi uchun kesh orqali.
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# ---------------------------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = False  # JWT header orqali ishlaydi, cookie kerak emas.
# Ommaviy API faqat o'qiydi va ariza qabul qiladi — o'chirish/yangilash yo'q.
# Ortiqcha metodni ochib qo'yish keraksiz hujum yuzasi.
CORS_ALLOW_METHODS = ["GET", "HEAD", "POST", "OPTIONS"]

# ---------------------------------------------------------------------------
# Xavfsizlik sarlavhalari (production.py da kuchaytiriladi)
# ---------------------------------------------------------------------------
# Tanishtiruv videosi shu manbalardan `iframe` bilan ko'rsatiladi. Ro'yxat
# ataylab qisqa: `useVideoModal.js` ham aynan shularni tanidi, boshqa havola
# oddiy tashqi havola bo'lib qoladi.
VIDEO_EMBED_ORIGINS = [
    "https://www.youtube-nocookie.com",
    "https://www.youtube.com",
    "https://player.vimeo.com",
]

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
# Sayt JWT bilan ishlaydi va CSRF tokenini JavaScript'dan o'qimaydi (faqat
# admin panelning o'z formalari ishlatadi, ular esa tokenni HTML ichidan
# oladi). Cookie'ni JS uchun yopish XSS holatida bitta qadamni qiyinlashtiradi.
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Content-Security-Policy (django-csp 4.x formati)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        # Tanishtiruv videosi: YouTube/Vimeo `iframe` ichida ochiladi. Bu
        # direktivalar bo'lmasa ular `default-src 'self'` ga tushib bloklanadi.
        "frame-src": ["'self'", *VIDEO_EMBED_ORIGINS],
        "media-src": ["'self'", "https:"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "object-src": ["'none'"],
    }
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Mars IT School <no-reply@marsit.uz>")
LEAD_NOTIFY_EMAILS = env.list("LEAD_NOTIFY_EMAILS", default=[])

# ---------------------------------------------------------------------------
# Loyihaga oid sozlamalar
# ---------------------------------------------------------------------------
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:5173")

# Saytda ro'yxatdan o'tish sahifasi yo'q — `/api/v1/auth/register/` ochiq
# qolsa u faqat spam hisob yaratish uchun ishlatiladigan hujum yuzasi bo'ladi.
# Kelajakda o'quvchi kabineti qo'shilsa shu qiymat True qilinadi.
PUBLIC_REGISTRATION_ENABLED = env.bool("PUBLIC_REGISTRATION_ENABLED", default=False)
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "axes": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        # Shaxsiy ma'lumotga murojaat, admin paneliga urinish, parol
        # o'zgartirish — hammasi shu kanalga tushadi. `INFO` darajasi
        # ataylab: bu voqealar hech qachon o'tkazib yuborilmasligi kerak.
        # Railway/monitoringda "security.audit" bo'yicha ogohlantirish
        # qo'yish uchun alohida logger sifatida ajratilgan.
        "security.audit": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
