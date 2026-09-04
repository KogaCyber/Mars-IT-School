from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.core.cache import PublicCacheMixin

from .models import Teacher
from .serializers import TeacherDetailSerializer, TeacherListSerializer


class TeacherViewSet(PublicCacheMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    # Sahifalashsiz: «Biz haqimizda» sahifasi o'qituvchilarni karuselda
    # to'liq ko'rsatadi va u yerda sahifalash boshqaruvi yo'q. Standart
    # 12 talik chegara bilan 13-o'qituvchi saytda umuman ko'rinmay qolardi.
    pagination_class = None
    search_fields = ("full_name", "position_ru", "company")

    def get_queryset(self):
        return Teacher.objects.published()

    def get_serializer_class(self):
        return TeacherDetailSerializer if self.action == "retrieve" else TeacherListSerializer
