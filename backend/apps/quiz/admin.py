from django.contrib import admin

from apps.core.translation import translated_fields, translation_fieldset

from .models import Option, Outcome, Question, Quiz, Submission


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ("order", *translated_fields("text"), "outcome", "skill", "weight")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "description_ru", "order", "is_published")}),
        translation_fieldset("title", "description"),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_ru", "quiz", "order")
    list_filter = ("quiz",)
    inlines = [OptionInline]
    fieldsets = (
        (None, {"fields": ("quiz", "text_ru", "image", "order")}),
        translation_fieldset("text"),
    )


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "code", "quiz")
    list_filter = ("quiz",)
    filter_horizontal = ("courses",)
    fieldsets = (
        (None, {"fields": ("quiz", "code", "title_ru", "description_ru", "image", "courses")}),
        translation_fieldset("title", "description"),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "full_name", "phone", "outcome")
    list_filter = ("quiz", "outcome", "created_at")
    readonly_fields = (
        "quiz",
        "outcome",
        "full_name",
        "phone",
        "answers",
        "scores",
        "skills",
        "created_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request) -> bool:
        return False
