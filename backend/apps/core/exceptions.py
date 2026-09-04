"""API xatoliklarini yagona formatga keltiruvchi handler."""

import logging

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context) -> Response | None:
    """Barcha API xatoliklarini `{"detail": ..., "errors": ...}` ko'rinishida qaytaradi.

    Kutilmagan xatoliklar loglanadi, lekin foydalanuvchiga ichki tafsilotlar
    (stack trace, SQL, fayl yo'llari) hech qachon ko'rsatilmaydi.
    """
    response = drf_exception_handler(exc, context)

    if response is None:
        if isinstance(exc, Http404):
            return Response({"detail": _("Topilmadi.")}, status=status.HTTP_404_NOT_FOUND)
        if isinstance(exc, PermissionDenied):
            return Response({"detail": _("Ruxsat yo'q.")}, status=status.HTTP_403_FORBIDDEN)
        if isinstance(exc, DjangoValidationError):
            # MongoDB backend'ida noto'g'ri ObjectId (masalan `/quiz-results/abc/`
            # yoki javoblardagi soxta savol kaliti) DRF bilmaydigan Django
            # `ValidationError` ko'taradi. Uni ushlamasak — foydalanuvchining
            # oddiy xatosi 500 bo'lib chiqardi va logni to'ldirardi.
            return Response(
                {
                    "detail": _("Ma'lumotlar noto'g'ri."),
                    "errors": {"detail": list(exc.messages)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.exception("Kutilmagan xatolik: %s", exc, exc_info=exc)
        return Response(
            {"detail": _("Serverda xatolik yuz berdi. Keyinroq urinib ko'ring.")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data

    # DRF `Http404` ni `NotFound` ga aylantirganda Django'ning o'z matnini
    # («No News matches the given query.») ichida olib qoladi. U tarjima
    # qilinmagan va model nomini oshkor qiladi — shuning uchun almashtiramiz.
    if response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = {"detail": _("Topilmadi.")}
        return response

    if isinstance(data, dict) and "detail" in data:
        response.data = {"detail": data["detail"]}
    elif isinstance(data, dict):
        response.data = {"detail": _("Ma'lumotlar noto'g'ri."), "errors": data}
    else:
        response.data = {"detail": _("Ma'lumotlar noto'g'ri."), "errors": data}

    return response
