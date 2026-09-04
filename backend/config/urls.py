"""Loyihaning asosiy URL konfiguratsiyasi.

URL'lar `SERVICE_ROLE` sozlamasiga qarab yig'iladi (config/settings/base.py):
admin panel va ommaviy API alohida portlarda ishlashi mumkin.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import health_view, staff_required
from apps.vacancies.views import resume_download_view

# Admin panel sarlavhalari va sahifalar bo'yicha guruhlash —
# `apps/core/admin_site.py` dagi `MarsAdminSite` ichida belgilangan.

api_v1 = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.courses.urls")),
    path("", include("apps.teachers.urls")),
    path("", include("apps.news.urls")),
    path("", include("apps.branches.urls")),
    path("", include("apps.vacancies.urls")),
    path("", include("apps.quiz.urls")),
    path("", include("apps.leads.urls")),
]

# /health/ ikkala rolda ham ochiq — Railway healthcheck har bir xizmatga tegadi.
urlpatterns = [path("health/", health_view, name="health")]

if settings.SERVICE_HAS_ADMIN:
    urlpatterns += [
        # DIQQAT — tartib muhim. `admin.site.urls` oxirida "hammasini ushlaydigan"
        # (catch-all) namuna bor, shuning uchun admin manzili ostidagi har qanday
        # o'z view'imiz undan OLDIN turishi shart; aks holda u 404 qaytaradi.
        #
        # Nomzod rezyumesi — faqat xodimga. Fayl `PRIVATE_MEDIA_ROOT` da yotadi
        # va statik uzatuvchiga ko'rinmaydi (apps/core/storage.py).
        path(
            f"{settings.ADMIN_URL}rezyume/<str:pk>/",
            resume_download_view,
            name="resume-download",
        ),
        path(settings.ADMIN_URL, admin.site.urls),
        # Admin paneldagi til almashtirgichi shu manzilga yuboradi
        # (`django.views.i18n.set_language` — tanlangan til seansda saqlanadi).
        path("i18n/", include("django.conf.urls.i18n")),
    ]

if settings.SERVICE_HAS_API:
    urlpatterns += [path("api/v1/", include((api_v1, "api"), namespace="v1"))]

# API hujjatlari. Ilgari ular faqat `DEBUG` da ochilardi, ya'ni productionda
# umuman yo'q edi va hamkorlar sxemani ko'ra olmasdi. Endi ular doim mavjud,
# lekin xodim huquqini talab qiladi — ommaga ochiq emas.
if settings.SERVICE_HAS_API:
    urlpatterns += [
        path("api/schema/", staff_required(SpectacularAPIView.as_view()), name="schema"),
        path(
            "api/docs/",
            staff_required(SpectacularSwaggerView.as_view(url_name="schema")),
            name="swagger-ui",
        ),
    ]

if settings.DEBUG:
    # Media fayllar admin panelda ham ko'rinishi kerak (rasm yuklash/preview).
    # Diqqat: bu faqat sayt rasmlari — rezyume `PRIVATE_MEDIA_ROOT` da.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        pass
    else:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
