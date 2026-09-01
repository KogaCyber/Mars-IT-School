from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("advantages", views.AdvantageViewSet, basename="advantage")
router.register("reviews", views.ParentReviewViewSet, basename="review")
router.register("faqs", views.FAQViewSet, basename="faq")
router.register("space-features", views.SpaceFeatureViewSet, basename="space-feature")
router.register("statistics", views.StatisticViewSet, basename="statistic")
router.register("founders", views.FounderViewSet, basename="founder")
router.register("future-benefits", views.FutureBenefitViewSet, basename="future-benefit")
router.register("child-skills", views.ChildSkillViewSet, basename="child-skill")
router.register(
    "project-defence-steps", views.ProjectDefenceStepViewSet, basename="project-defence-step"
)
router.register("school-features", views.SchoolFeatureViewSet, basename="school-feature")

urlpatterns = [
    path("site-settings/", views.site_settings_view, name="site-settings"),
    path("home/", views.home_bootstrap_view, name="home-bootstrap"),
    path("", include(router.urls)),
]
