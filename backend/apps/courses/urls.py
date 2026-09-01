from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, DirectionViewSet

router = DefaultRouter()
router.register("directions", DirectionViewSet, basename="direction")
router.register("courses", CourseViewSet, basename="course")

urlpatterns = [path("", include(router.urls))]
