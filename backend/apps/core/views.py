"""Umumiy kontent uchun faqat o'qish API'lari."""

import logging

from django.db import connections
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .cache import PublicCacheMixin, public_cache
from .models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
    SiteSettings,
    SpaceFeature,
    Statistic,
)
from .serializers import (
    AdvantageSerializer,
    ChildSkillSerializer,
    FAQSerializer,
    FounderSerializer,
    FutureBenefitSerializer,
    ParentReviewSerializer,
    ProjectDefenceStepSerializer,
    SchoolFeatureSerializer,
    SiteSettingsSerializer,
    SpaceFeatureSerializer,
    StatisticSerializer,
)

logger = logging.getLogger(__name__)


class PublicReadOnlyViewSet(PublicCacheMixin, viewsets.ReadOnlyModelViewSet):
    """Chop etilgan yozuvlarni hammaga ochiq qaytaradigan bazaviy viewset."""

    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return self.queryset.published()


class AdvantageViewSet(PublicReadOnlyViewSet):
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer


class ParentReviewViewSet(PublicReadOnlyViewSet):
    queryset = ParentReview.objects.all()
    serializer_class = ParentReviewSerializer


class FAQViewSet(PublicReadOnlyViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class SpaceFeatureViewSet(PublicReadOnlyViewSet):
    queryset = SpaceFeature.objects.all()
    serializer_class = SpaceFeatureSerializer


class StatisticViewSet(PublicReadOnlyViewSet):
    queryset = Statistic.objects.all()
    serializer_class = StatisticSerializer


class FounderViewSet(PublicReadOnlyViewSet):
    queryset = Founder.objects.all()
    serializer_class = FounderSerializer


class FutureBenefitViewSet(PublicReadOnlyViewSet):
    queryset = FutureBenefit.objects.all()
    serializer_class = FutureBenefitSerializer


class ChildSkillViewSet(PublicReadOnlyViewSet):
    queryset = ChildSkill.objects.all()
    serializer_class = ChildSkillSerializer


class ProjectDefenceStepViewSet(PublicReadOnlyViewSet):
    queryset = ProjectDefenceStep.objects.all()
    serializer_class = ProjectDefenceStepSerializer


class SchoolFeatureViewSet(PublicReadOnlyViewSet):
    queryset = SchoolFeature.objects.all()
    serializer_class = SchoolFeatureSerializer


@extend_schema(responses=SiteSettingsSerializer)
@public_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def site_settings_view(request):
    """Sayt kontaktlari va ijtimoiy tarmoqlari."""
    serializer = SiteSettingsSerializer(SiteSettings.load(), context={"request": request})
    return Response(serializer.data)


@extend_schema(responses=OpenApiTypes.OBJECT)
@public_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def home_bootstrap_view(request):
    """Bosh sahifa uchun barcha kontent — bitta so'rovda.

    Ilgari bosh sahifa 6 ta alohida so'rov yuborardi (afzalliklar, fikrlar,
    FAQ, o'qituvchilar, yangiliklar, sozlamalar). Har bir so'rov Railway ↔ Atlas
    kechikishi sabab ~1 soniya turardi va brauzer ularni parallel yuborsa ham
    gunicorn worker'lari navbatga qo'yardi. Endi hammasi bitta javobda keladi.
    """
    from apps.news.models import News
    from apps.news.serializers import NewsListSerializer
    from apps.teachers.models import Teacher
    from apps.teachers.serializers import TeacherListSerializer

    ctx = {"request": request}
    return Response(
        {
            "settings": SiteSettingsSerializer(SiteSettings.load(), context=ctx).data,
            "advantages": AdvantageSerializer(
                Advantage.objects.published(), many=True, context=ctx
            ).data,
            "reviews": ParentReviewSerializer(
                ParentReview.objects.published(), many=True, context=ctx
            ).data,
            "faqs": FAQSerializer(FAQ.objects.published(), many=True, context=ctx).data,
            "teachers": TeacherListSerializer(
                Teacher.objects.published()[:12], many=True, context=ctx
            ).data,
            "news": NewsListSerializer(
                News.objects.published()
                .filter(published_at__lte=timezone.now())
                .select_related("category")[:9],
                many=True,
                context=ctx,
            ).data,
        }
    )


@extend_schema(responses={200: None, 503: None})
@api_view(["GET"])
@permission_classes([AllowAny])
def health_view(request):
    """Railway healthcheck uchun: MongoDB bilan aloqani ham tekshiradi.

    Baza ishlamayotgan bo'lsa 503 qaytariladi — shunda Railway buzuq deploy'ga
    trafik yubormaydi va konteynerni qayta ishga tushiradi. 200 qaytarsak,
    sayt tashqaridan "sog'lom" ko'rinib, aslida hech nima ishlamas edi.
    """
    try:
        # MongoDB'ning standart tekshiruvi — `ping` buyrug'i.
        connections["default"].database.client.admin.command("ping")
        db_ok = True
    except Exception:  # noqa: BLE001 — healthcheck hech qachon stack trace bermasligi kerak
        logger.exception("Healthcheck: MongoDB bilan aloqa yo'q")
        db_ok = False

    return Response(
        {"status": "ok" if db_ok else "degraded", "database": db_ok},
        status=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
