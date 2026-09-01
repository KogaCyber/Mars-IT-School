from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.core.cache import PublicCacheMixin

from .filters import CourseFilter
from .models import Course, Direction
from .serializers import CourseDetailSerializer, CourseListSerializer, DirectionSerializer


class DirectionViewSet(PublicCacheMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DirectionSerializer
    lookup_field = "slug"
    pagination_class = None
    queryset = Direction.objects.all()

    def get_queryset(self):
        return Direction.objects.published()


class CourseViewSet(PublicCacheMixin, ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_class = CourseFilter
    search_fields = ("title_ru", "subtitle_ru", "description_ru")
    ordering_fields = ("order", "price", "created_at")
    pagination_class = None

    def get_queryset(self):
        # MongoDB backend'i `prefetch_related()` ni qo'llab-quvvatlamaydi —
        # bog'liq yozuvlar (o'qituvchilar, bosqichlar) serializerda o'qiladi.
        return Course.objects.published().select_related("direction")

    def get_serializer_class(self):
        return CourseDetailSerializer if self.action == "retrieve" else CourseListSerializer
