from pathlib import Path

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

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
        (_("Matn"), {"fields": ("description_ru", "requirements_ru", "conditions_ru")}),
        (_("Maosh"), {"fields": (("salary_from", "salary_to"), "salary_currency")}),
        (_("Chop etish"), {"fields": ("order", "is_open", "is_published")}),
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
        "resume_link",
        "resume_url",
        "ip_address",
        "created_at",
        "updated_at",
    )
    fields = readonly_fields + ("status",)

    def has_add_permission(self, request) -> bool:
        return False

    @admin.display(description=_("rezyume"))
    def resume_link(self, obj):
        """Rezyumeni ko'rish havolasi.

        Fayl `PRIVATE_MEDIA_ROOT` ichida — uning ommaviy manzili YO'Q va
        `obj.resume.url` ataylab xatolik beradi. Faylga yagona yo'l — xodim
        huquqini tekshiradigan `resume-download` view.

        PDF yangi oynada ochiladi: uni ko'rish uchun kompyuterga yuklab olish
        shart emas. Yonidagi kichik havola esa kerak bo'lsa faylni yuklab
        oladi (doc/docx/rtf uchun brauzer baribir shuni qiladi).
        """
        if not obj.resume:
            return "—"

        url = reverse("resume-download", args=[obj.pk])
        suffix = Path(obj.resume.name).suffix.lower()

        # doc/docx/rtf ni brauzer ocholmaydi — ular uchun bitta havola yetarli.
        if suffix != ".pdf":
            return format_html('<a href="{}">{}</a>', url, _("Yuklab olish"))

        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>'
            '<span style="color:#999"> · </span>'
            '<a href="{}?download=1" style="color:#999">{}</a>',
            url,
            _("Ochish (yangi oynada)"),
            url,
            _("yuklab olish"),
        )
