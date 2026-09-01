from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Branch
from .serializers import BranchDetailSerializer, BranchListSerializer


class BranchViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = None
    search_fields = ("name_ru", "address_ru")

    def get_queryset(self):
        return Branch.objects.published()

    def get_serializer_class(self):
        return BranchDetailSerializer if self.action == "retrieve" else BranchListSerializer
