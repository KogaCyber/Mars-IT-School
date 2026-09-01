from django.db.models import F
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import News, NewsCategory
from .serializers import NewsCategorySerializer, NewsDetailSerializer, NewsListSerializer


class NewsCategoryViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = NewsCategorySerializer
    lookup_field = "slug"
    pagination_class = None
    queryset = NewsCategory.objects.all()

    def get_queryset(self):
        return NewsCategory.objects.published()


class NewsViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_fields = ["category__slug", "is_featured"]
    search_fields = ("title_ru", "excerpt_ru", "body_ru")
    ordering_fields = ("published_at", "views_count")

    def get_queryset(self):
        return (
            News.objects.published()
            .filter(published_at__lte=timezone.now())
            .select_related("category")
        )

    def get_serializer_class(self):
        return NewsDetailSerializer if self.action == "retrieve" else NewsListSerializer

    def retrieve(self, request, *args, **kwargs):
        news = self.get_object()
        # Ko'rishlar sonini poyga holatisiz (race-free) oshiramiz.
        News.objects.filter(pk=news.pk).update(views_count=F("views_count") + 1)
        news.views_count += 1
        return Response(self.get_serializer(news).data)
