"""Umumiy kontent uchun faqat o'qish API'lari."""

import functools
import logging

from django.core.exceptions import PermissionDenied
from django.db import connections
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .cache import PublicCacheMixin, public_cache
from .models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    PageSection,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
    SiteSettings,
    SpaceFeature,
    Statistic,
)
from .revision import current_revision
from .serializers import (
    AdvantageSerializer,
    ChildSkillSerializer,
    FAQSerializer,
    FounderSerializer,
    FutureBenefitSerializer,
    PageSectionSerializer,
    ParentReviewSerializer,
    ProjectDefenceStepSerializer,
    SchoolFeatureSerializer,
    SiteSettingsSerializer,
    SpaceFeatureSerializer,
    StatisticSerializer,
)

logger = logging.getLogger(__name__)
audit_log = logging.getLogger("security.audit")

#: Bosh sahifa javobidagi har bir ro'yxatning eng ko'p elementi.
HOME_SECTION_LIMIT = 24


def staff_required(view):
    """Faqat tizimga kirgan xodim uchun.

    `django.contrib.admin.views.decorators.staff_member_required` login
    sahifasiga yo'naltiradi — bu shaxsiy faylni so'ragan bot uchun "manzil
    mavjud" degan ma'lumot beradi. Bu yerda esa kirmagan foydalanuvchi ham,
    xodim bo'lmagan foydalanuvchi ham bir xil 403 oladi.
    """

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated and user.is_active and user.is_staff):
            # Xodimga mo'ljallangan manzilga urinish — o'z-o'zidan shubhali
            # voqea. Qayd etilmasa, sekin va uzoq davom etadigan qidiruvni
            # (manzillarni birma-bir sinab ko'rish) hech kim sezmasdi.
            audit_log.warning(
                "Xodim huquqisiz murojaat: path=%s user=%s",
                request.path,
                getattr(user, "email", "anonim"),
            )
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


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
    # Har bir bo'limga aniq chegara qo'yiladi. Bosh sahifa bularning hammasini
    # baribir bitta ekranda ko'rsatadi, lekin admin panelda 200 ta savol-javob
    # yig'ilib qolsa javob hajmi jimgina o'sib ketardi — va bu eng ko'p
    # so'raladigan manzil.
    return Response(
        {
            "settings": SiteSettingsSerializer(SiteSettings.load(), context=ctx).data,
            # Bosh sahifa bloklarining matni va rasmlari (admin panelda tahrirlanadi).
            "sections": _sections_payload(request, pages=["home", "common"]),
            "advantages": AdvantageSerializer(
                Advantage.objects.published()[:HOME_SECTION_LIMIT], many=True, context=ctx
            ).data,
            "reviews": ParentReviewSerializer(
                ParentReview.objects.published()[:HOME_SECTION_LIMIT], many=True, context=ctx
            ).data,
            "faqs": FAQSerializer(
                FAQ.objects.published()[:HOME_SECTION_LIMIT], many=True, context=ctx
            ).data,
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


class RevisionThrottle(ScopedRateThrottle):
    scope = "revision"


class HealthThrottle(ScopedRateThrottle):
    scope = "health"


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([AllowAny])
# Umumiy `anon` limiti (60/min) bu yerga to'g'ri kelmaydi: sayt manzilni har 5
# soniyada so'raydi (12/min) va bitta NAT ortidagi bir necha tashrifchi umumiy
# limitni to'ldirib qo'yardi. Shuning uchun alohida, kengroq limit — lekin
# butunlay cheklovsiz emas: aks holda bu manzil DoS kuchaytirgichi bo'lardi.
@throttle_classes([RevisionThrottle])
def revision_view(request):
    """Kontentning joriy versiyasi — sayt jonli yangilanishi uchun.

    Sayt shu manzilni qisqa oraliqda so'rab turadi va raqam o'zgarishi bilan
    kontentni qayta yuklaydi (`apps/core/revision.py` ga qarang). Javob hech
    qayerda keshlanmasligi kerak — aks holda o'zgarish sezilmay qolardi.
    """
    response = Response({"revision": current_revision()})
    response["Cache-Control"] = "no-store"
    return response


@extend_schema(responses={200: None, 503: None})
@api_view(["GET"])
@permission_classes([AllowAny])
# Alohida limit: Railway healthcheck va monitoring umumiy `anon` hisobini
# to'ldirib, haqiqiy tashrifchilarni siqib chiqarmasligi kerak.
@throttle_classes([HealthThrottle])
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


def _sections_payload(request, pages=None) -> dict:
    """Sahifa bo'limlarini `{"home.hero": {...}}` ko'rinishida qaytaradi.

    Sayt bo'limni kaliti bo'yicha oladi. Bo'sh maydon javobda ham bo'sh qoladi —
    frontend bunday joyda maketdagi standart matnni ko'rsatadi, ya'ni admin
    panelda hech narsa yozilmagan bo'lim ham to'g'ri ko'rinadi.
    """
    queryset = PageSection.objects.filter(is_published=True).prefetch_related("items")
    if pages:
        queryset = queryset.filter(page__in=pages)

    serializer = PageSectionSerializer(queryset, many=True, context={"request": request})
    return {item["key"]: item for item in serializer.data}


@extend_schema(responses=OpenApiTypes.OBJECT)
@public_cache
@api_view(["GET"])
@permission_classes([AllowAny])
def content_view(request):
    """Barcha sahifalarning matn/rasm bo'limlari — bitta so'rovda.

    Sayt ochilganda bir marta yuklanadi: bo'limlar soni oz va hajmi kichik,
    shuning uchun sahifama-sahifa so'rash tarmoqqa ortiqcha yuk bo'lardi.
    """
    return Response(_sections_payload(request))
