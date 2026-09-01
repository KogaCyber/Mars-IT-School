from django.contrib import admin

from apps.core.translation import translation_fieldset

from .models import Vacancy, VacancyApplication


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "branch", "employment_type", "is_open", "is_published")
    list_filter = ("employment_type", "is_open", "is_published", "branch")
    list_editable = ("is_open", "is_published")
    search_fields = ("title_ru", "description_ru")
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "branch", "employment_type", "icon_name")}),
        ("Matn", {"fields": ("description_ru", "requirements_ru", "conditions_ru")}),
        ("Maosh", {"fields": ("salary_from", "salary_to")}),
        ("Chop etish", {"fields": ("order", "is_open", "is_published")}),
        translation_fieldset("title", "description", "requirements", "conditions"),
    )


@admin.register(VacancyApplication)
class VacancyApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "vacancy", "phone", "status", "created_at")
    list_filter = ("status", "vacancy", "created_at")
    search_fields = ("full_name", "phone", "email")
    date_hierarchy = "created_at"
    readonly_fields = (
        "vacancy",
        "full_name",
        "phone",
        "email",
        "cover_letter",
        "resume",
        "resume_url",
        "ip_address",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields + ("status",)

    def has_add_permission(self, request) -> bool:
        return False
