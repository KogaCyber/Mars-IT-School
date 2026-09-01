from rest_framework import serializers

from apps.core.drf import TranslatedSerializerMixin

from .models import Skill, Teacher


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "icon")


class TeacherListSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    """Bosh sahifadagi kartochka uchun to'liq ma'lumot."""

    translated_fields = ("position", "bio")
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = (
            "id",
            "slug",
            "full_name",
            "photo",
            "badge",
            "company",
            "company_logo",
            "experience_years",
            "students_count",
            "skills",
        )


class TeacherDetailSerializer(TeacherListSerializer):
    courses = serializers.SerializerMethodField()

    class Meta(TeacherListSerializer.Meta):
        fields = TeacherListSerializer.Meta.fields + (
            "telegram_url",
            "linkedin_url",
            "instagram_url",
            "courses",
        )

    def get_courses(self, obj) -> list[dict]:
        return [
            {"id": str(course.pk), "slug": course.slug, "title": course.tr("title", self.language)}
            for course in obj.courses.published()
        ]
