from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.translation import translation_fieldset

from .models import Skill, Teacher


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "position_ru", "badge", "students_count", "order", "is_published",
    )
    list_editable = ("order", "is_published")
    search_fields = ("full_name", "position_ru", "company")
    filter_horizontal = ("skills",)
    fieldsets = (
        (None, {"fields": ("full_name", "slug", "photo", "position_ru", "badge", "bio_ru")}),
        (
            _("Tajriba"),
            {"fields": ("company", "company_logo", "experience_years", "students_count")},
        ),
        (_("Texnologiyalar"), {"fields": ("skills",)}),
        (_("Havolalar"), {"fields": ("telegram_url", "linkedin_url", "instagram_url")}),
        (_("Chop etish"), {"fields": ("order", "is_published")}),
        translation_fieldset("position", "bio"),
    )
