from django.contrib import admin

from apps.core.translation import translation_fieldset

from .models import Course, CourseFeature, CourseStage, Direction


class CourseFeatureInline(admin.StackedInline):
    model = CourseFeature
    extra = 0
    fields = ("order", "title_ru", "description_ru", "icon")


class CourseStageInline(admin.StackedInline):
    model = CourseStage
    extra = 0
    fields = ("order", "number", "title_ru", "description_ru", "duration_months", "image")


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
    inlines = [CourseFeatureInline, CourseStageInline]
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "direction", "subtitle_ru", "description_ru")}),
        ("Ko'rinish", {"fields": ("card_image", "hero_image", "accent_color")}),
        (
            "Shartlar",
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
        ("O'qituvchilar", {"fields": ("teachers",)}),
        ("Chop etish", {"fields": ("order", "is_featured", "is_published")}),
        translation_fieldset("title", "subtitle", "description"),
    )
