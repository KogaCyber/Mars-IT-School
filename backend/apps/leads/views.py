from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import Lead
from .serializers import LeadCreateSerializer
from .services import notify_new_lead
from .utils import client_ip


class LeadCreateView(CreateAPIView):
    """Saytdagi barcha formalardan ariza qabul qiladi (faqat POST)."""

    queryset = Lead.objects.all()
    serializer_class = LeadCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "lead"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save(
            ip_address=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
        notify_new_lead(lead)
        return Response(
            {"detail": "Arizangiz qabul qilindi. Tez orada bog'lanamiz."},
            status=status.HTTP_201_CREATED,
        )
