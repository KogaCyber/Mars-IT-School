from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Teacher
from .serializers import TeacherDetailSerializer, TeacherListSerializer


class TeacherViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    search_fields = ("full_name", "position_ru", "company")

    def get_queryset(self):
        return Teacher.objects.published()

    def get_serializer_class(self):
        return TeacherDetailSerializer if self.action == "retrieve" else TeacherListSerializer
