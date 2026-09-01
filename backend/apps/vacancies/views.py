from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.core.cache import PublicCacheMixin
from apps.leads.utils import client_ip

from .models import Vacancy, VacancyApplication
from .serializers import (
    VacancyApplicationSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)


class VacancyViewSet(PublicCacheMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = None
    search_fields = ("title_ru", "description_ru")

    def get_queryset(self):
        return Vacancy.objects.published().filter(is_open=True).select_related("branch")

    def get_serializer_class(self):
        return VacancyDetailSerializer if self.action == "retrieve" else VacancyListSerializer


class VacancyApplicationCreateView(CreateAPIView):
    """«Вакансия / Заявка» formasi. Fayl yuklash uchun multipart qabul qilinadi."""

    queryset = VacancyApplication.objects.all()
    serializer_class = VacancyApplicationSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "lead"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ip_address=client_ip(request))
        return Response(
            {"detail": "Arizangiz qabul qilindi. Tez orada bog'lanamiz."},
            status=status.HTTP_201_CREATED,
        )
