"""Loyihaning asosiy URL konfiguratsiyasi.

URL'lar `SERVICE_ROLE` sozlamasiga qarab yig'iladi (config/settings/base.py):
admin panel va ommaviy API alohida portlarda ishlashi mumkin.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import health_view

# Admin panel sarlavhalari
admin.site.site_header = "Mars IT School — boshqaruv paneli"
admin.site.site_title = "Mars IT School"
admin.site.index_title = "Boshqaruv"

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
    urlpatterns += [path(settings.ADMIN_URL, admin.site.urls)]

if settings.SERVICE_HAS_API:
    urlpatterns += [path("api/v1/", include((api_v1, "api"), namespace="v1"))]

if settings.DEBUG:
    if settings.SERVICE_HAS_API:
        urlpatterns += [
            path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
            path(
                "api/docs/",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
        ]

    # Media fayllar admin panelda ham ko'rinishi kerak (rasm yuklash/preview).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        pass
    else:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
