from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.translation import translated_fields, translation_fieldset

from .models import Course, CourseFaq, CourseFeature, CourseStage, Direction


class CourseFeatureInline(admin.StackedInline):
    model = CourseFeature
    extra = 0
    fields = ("order", *translated_fields("title", "description"), "icon")


class CourseStageInline(admin.StackedInline):
    model = CourseStage
    extra = 0
    fields = (
        "order", "number", *translated_fields("title", "description"),
        "duration_months", "image",
    )


class CourseFaqInline(admin.StackedInline):
    """Kurs sahifasining pastidagi savol-javoblar — shu kursning o'z ichida."""

    model = CourseFaq
    extra = 0
    fields = ("order", *translated_fields("question", "answer"))
    verbose_name = _("Savol-javob")
    verbose_name_plural = _("Savol-javoblar (sahifaning pastida)")


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "description_ru", "icon", "order", "is_published")}),
        translation_fieldset("title", "description"),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "direction", "age_range", "price", "is_featured", "is_published")
    list_filter = ("direction", "is_featured", "is_published")
    list_select_related = ("direction",)
    list_editable = ("is_featured", "is_published")
    search_fields = ("title_ru", "subtitle_ru")
    filter_horizontal = ("teachers",)
    inlines = [CourseFeatureInline, CourseStageInline, CourseFaqInline]
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "direction", "subtitle_ru", "description_ru")}),
        (_("Ko'rinish"), {"fields": ("card_image", "hero_image", "accent_color")}),
        (
            _("Shartlar"),
            {
                "fields": (
                    "age_from",
                    "age_to",
                    "duration_months",
                    "lessons_per_week",
                    "lesson_duration_minutes",
                    "price",
                )
            },
        ),
        (_("O'qituvchilar"), {"fields": ("teachers",)}),
        (_("Chop etish"), {"fields": ("order", "is_featured", "is_published")}),
        translation_fieldset("title", "subtitle", "description"),
    )
