from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsCategoryViewSet, NewsViewSet

router = DefaultRouter()
router.register("news-categories", NewsCategoryViewSet, basename="news-category")
router.register("news", NewsViewSet, basename="news")

urlpatterns = [path("", include(router.urls))]
