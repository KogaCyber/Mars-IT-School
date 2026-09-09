import contextlib
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


def _is_pdf(handle) -> bool:
    """Fayl haqiqatan ham PDF bilan boshlanadimi (kursor joyiga qaytariladi)."""
    try:
        handle.seek(0)
        header = handle.read(4)
    except OSError:
        return False
    finally:
        with contextlib.suppress(OSError):
            handle.seek(0)
    return header == b"%PDF"


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

    PDF brauzerda **ochib** ko'rsatiladi (yangi oyna): xodim rezyumeni ko'rish
    uchun uni kompyuteriga yuklab olishi shart emas — bu ham qulayroq, ham
    xavfsizroq (nusxa diskda qolmaydi). Qolgan turlarni (doc/docx/rtf) brauzer
    baribir chiza olmaydi, shuning uchun ular avvalgidek yuklab olinadi.
    `?download=1` bilan PDF ham majburan yuklab olinadi.
    """
    application = get_object_or_404(VacancyApplication, pk=pk)
    if not application.resume:
        raise Http404(_("Rezyume yuklanmagan."))

    try:
        handle = application.resume.open("rb")
    except FileNotFoundError as exc:  # fayl volume'dan yo'qolgan bo'lishi mumkin
        raise Http404(_("Fayl topilmadi.")) from exc

    # Fayl diskda tasodifiy nom bilan yotadi; yuklab olishda esa xodim uchun
    # tushunarli nom beriladi. Kengaytma faqat oq ro'yxatdan olinadi —
    # `Content-Disposition` ga ixtiyoriy satr tushishi mumkin emas.
    suffix = Path(application.resume.name).suffix.lower()
    if suffix not in RESUME_SIGNATURES:
        suffix = ".bin"

    # Brauzerda ochish faqat PDF uchun va faqat fayl haqiqatan ham PDF bo'lsa.
    # Signatura yuklashda bir marta tekshirilgan, lekin bu yerda qayta
    # tekshiriladi: `.pdf` deb nomlangan HTML admin domenida ochilib ketmasin.
    inline = suffix == ".pdf" and request.GET.get("download") != "1" and _is_pdf(handle)

    audit_log.info(
        "Rezyume %s: application=%s kandidat=%s xodim=%s ip=%s",
        "ochildi" if inline else "yuklab olindi",
        application.pk,
        application.full_name,
        request.user.email,
        client_ip(request),
    )

    response = FileResponse(
        handle,
        # `as_attachment=False` — brauzer PDF'ni o'z ko'ruvchisida ochadi.
        # Boshqa turlar uchun `True`: HTML yoki SVG ko'rinishidagi fayl admin
        # domenida bajarilib ketishining oldini oladi.
        as_attachment=not inline,
        filename=f"rezyume-{application.pk}{suffix}",
        # Turi aniq ko'rsatiladi (`nosniff` bilan birga) — brauzer mazmunga
        # qarab «taxmin qilmaydi» va PDF'ni HTML deb o'qimaydi.
        content_type="application/pdf" if inline else "application/octet-stream",
    )
    response["X-Content-Type-Options"] = "nosniff"
    # Ochilayotgan PDF uchun `sandbox` qo'yilmaydi: u brauzerning o'z PDF
    # ko'ruvchisini ishga tushirmay qo'yishi mumkin. Tashqi resurs yuklash
    # esa baribir taqiqlangan.
    response["Content-Security-Policy"] = (
        "default-src 'none'" if inline else "default-src 'none'; sandbox"
    )
    return response
