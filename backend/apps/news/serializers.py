from rest_framework import serializers

from apps.core.drf import TranslatedSerializerMixin

from .models import News, NewsCategory, NewsImage


class NewsCategorySerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title",)

    class Meta:
        model = NewsCategory
        fields = ("id", "slug")


class NewsImageSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("caption",)

    class Meta:
        model = NewsImage
        fields = ("id", "image", "order")


class NewsListSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "excerpt")
    category = NewsCategorySerializer(read_only=True)

    class Meta:
        model = News
        fields = (
            "id",
            "slug",
            "cover",
            "category",
            "published_at",
            "reading_minutes",
            "views_count",
            "is_featured",
        )


class NewsDetailSerializer(NewsListSerializer):
    translated_fields = ("title", "excerpt", "body")
    gallery = NewsImageSerializer(many=True, read_only=True)

    class Meta(NewsListSerializer.Meta):
        fields = NewsListSerializer.Meta.fields + ("gallery",)
