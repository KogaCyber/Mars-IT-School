from rest_framework import serializers

from apps.core.drf import TranslatedSerializerMixin

from .models import Branch, BranchImage


class BranchImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchImage
        fields = ("id", "image", "order")


class BranchListSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("name", "address", "landmark", "working_hours")

    class Meta:
        model = Branch
        fields = (
            "id",
            "slug",
            "phone",
            "latitude",
            "longitude",
            "map_url_yandex",
            "map_url_google",
            "cover",
            "is_main",
        )


class BranchDetailSerializer(BranchListSerializer):
    gallery = BranchImageSerializer(many=True, read_only=True)

    class Meta(BranchListSerializer.Meta):
        fields = BranchListSerializer.Meta.fields + ("gallery",)
