import logging
from pathlib import Path

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.core.cache import PublicCacheMixin
from apps.core.uploads import RESUME_SIGNATURES
from apps.core.views import staff_required
from apps.leads.utils import client_ip

from .models import Vacancy, VacancyApplication
from .serializers import (
    VacancyApplicationSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)

#: Shaxsiy ma'lumotga murojaat aynan shu loggerga yoziladi — uni monitoringda
#: alohida kuzatish mumkin (kim, qachon, kimning hujjatini oldi).
audit_log = logging.getLogger("security.audit")


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
            {"detail": _("Arizangiz qabul qilindi. Tez orada bog'lanamiz.")},
            status=status.HTTP_201_CREATED,
        )


@require_safe
@never_cache
@staff_required
def resume_download_view(request, pk: str):
    """Nomzod rezyumesini FAQAT xodimga beradi.

    Fayl `PRIVATE_MEDIA_ROOT` ichida yotadi va hech qanday statik uzatuvchi
    (WhiteNoise) uni ko'rmaydi — yagona yo'l shu view. Admin paneldagi
    «Rezyume» havolasi shu manzilga ishora qiladi.

    Manzilda arizaning ObjectId'si turadi, fayl nomi emas: nomzodning ismi
    manzilda ko'rinmaydi va boshqa faylni so'rab olish mumkin emas.
    """
    application = get_object_or_404(VacancyApplication, pk=pk)
    if not application.resume:
        raise Http404(_("Rezyume yuklanmagan."))

    try:
        handle = application.resume.open("rb")
    except FileNotFoundError as exc:  # fayl volume'dan yo'qolgan bo'lishi mumkin
        raise Http404(_("Fayl topilmadi.")) from exc

    # Shaxsiy ma'lumotga har bir murojaat qayd etiladi. Bu ma'lumotlar
    # sizib chiqqan taqdirda «kim ko'rgan» degan savolga javob beradigan
    # yagona manba — hujjat yuklab olingandan keyin uni kuzatib bo'lmaydi.
    audit_log.info(
        "Rezyume yuklab olindi: application=%s kandidat=%s xodim=%s ip=%s",
        application.pk,
        application.full_name,
        request.user.email,
        client_ip(request),
    )

    # Fayl diskda tasodifiy nom bilan yotadi; yuklab olishda esa xodim uchun
    # tushunarli nom beriladi. Kengaytma faqat oq ro'yxatdan olinadi —
    # `Content-Disposition` ga ixtiyoriy satr tushishi mumkin emas.
    suffix = Path(application.resume.name).suffix.lower()
    if suffix not in RESUME_SIGNATURES:
        suffix = ".bin"

    response = FileResponse(
        handle,
        # `as_attachment` — brauzer faylni ochib emas, yuklab oladi. Bu HTML
        # yoki SVG ko'rinishidagi fayl admin domenida bajarilib ketishining
        # oldini oladi.
        as_attachment=True,
        filename=f"rezyume-{application.pk}{suffix}",
        # Turi baribir aniqlanmasin: brauzer mazmunga qarab «taxmin qilmaydi».
        content_type="application/octet-stream",
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return response
