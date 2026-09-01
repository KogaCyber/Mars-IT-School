from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import VacancyApplicationCreateView, VacancyViewSet

router = DefaultRouter()
router.register("vacancies", VacancyViewSet, basename="vacancy")

urlpatterns = [
    path(
        "vacancy-applications/",
        VacancyApplicationCreateView.as_view(),
        name="vacancy-application-create",
    ),
    path("", include(router.urls)),
]
