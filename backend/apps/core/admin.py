from django.contrib import admin

from .models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
    SiteSettings,
    SpaceFeature,
    Statistic,
)
from .translation import translation_fieldset


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("phone", "email")

    def has_add_permission(self, request) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ("number", "title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title_ru", "description_ru")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "number", "title_ru", "description_ru", "image", "order", "is_published",
                )
            },
        ),
        translation_fieldset("title", "description"),
    )


@admin.register(ParentReview)
class ParentReviewAdmin(admin.ModelAdmin):
    list_display = ("full_name", "relation_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("full_name", "text_ru")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name", "relation_ru", "photo", "video_url", "text_ru",
                    "order", "is_published",
                )
            },
        ),
        translation_fieldset("text", "relation"),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("question_ru", "answer_ru")
    fieldsets = (
        (None, {"fields": ("question_ru", "answer_ru", "order", "is_published")}),
        translation_fieldset("question", "answer"),
    )


@admin.register(SpaceFeature)
class SpaceFeatureAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title_ru", "description_ru", "icon", "screenshot", "order", "is_published",
                )
            },
        ),
        translation_fieldset("title", "description"),
    )


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("value", "label_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (None, {"fields": ("value", "label_ru", "order", "is_published")}),
        translation_fieldset("label"),
    )


@admin.register(Founder)
class FounderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "full_name", "photo", "position_ru", "bio_ru",
                    "order", "is_published",
                )
            },
        ),
        translation_fieldset("position", "bio"),
    )


@admin.register(FutureBenefit)
class FutureBenefitAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "description_ru", "icon", "order", "is_published")}),
        translation_fieldset("title", "description"),
    )


@admin.register(ChildSkill)
class ChildSkillAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "icon_name", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title_ru", "description_ru", "icon_name", "icon", "order", "is_published",
                )
            },
        ),
        translation_fieldset("title", "description"),
    )


@admin.register(ProjectDefenceStep)
class ProjectDefenceStepAdmin(admin.ModelAdmin):
    list_display = ("label_ru", "title_ru", "icon_name", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "label_ru", "title_ru", "description_ru", "icon_name",
                    "order", "is_published",
                )
            },
        ),
        translation_fieldset("label", "title", "description"),
    )


@admin.register(SchoolFeature)
class SchoolFeatureAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "order", "is_published")}),
        translation_fieldset("title"),
    )
