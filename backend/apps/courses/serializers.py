from rest_framework import serializers

from apps.core.drf import TranslatedSerializerMixin
from apps.teachers.serializers import TeacherListSerializer

from .models import Course, CourseFeature, CourseStage, Direction


class DirectionSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = Direction
        fields = ("id", "slug", "icon")


class CourseFeatureSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = CourseFeature
        fields = ("id", "icon", "order")


class CourseStageSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = CourseStage
        fields = ("id", "number", "image", "duration_months", "order")


class CourseListSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "subtitle")
    direction = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    age_range = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "slug",
            "card_image",
            "accent_color",
            "age_from",
            "age_to",
            "age_range",
            "duration_months",
            "lessons_per_week",
            "price",
            "is_featured",
            "direction",
        )


class CourseDetailSerializer(CourseListSerializer):
    translated_fields = ("title", "subtitle", "description")
    teachers = TeacherListSerializer(many=True, read_only=True)
    features = CourseFeatureSerializer(many=True, read_only=True)
    stages = CourseStageSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + (
            "hero_image",
            "lesson_duration_minutes",
            "teachers",
            "features",
            "stages",
        )
