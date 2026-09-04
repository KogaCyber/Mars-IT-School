from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from apps.core.translation import translation_fieldset

from .models import Branch, BranchImage
from .services import resolve_coordinates


class BranchImageInline(admin.TabularInline):
    model = BranchImage
    extra = 1
    fields = ("order", "image")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "address_ru", "coordinates", "phone", "is_main", "is_published")
    list_editable = ("is_main", "is_published")
    search_fields = ("name_ru", "address_ru")
    inlines = [BranchImageInline]
    fieldsets = (
        (None, {"fields": ("name_ru", "slug", "address_ru", "landmark_ru", "cover")}),
        (_("Aloqa"), {"fields": ("phone", "working_hours_ru")}),
        (
            _("Xarita"),
            {
                "fields": ("map_url_yandex", "map_url_google", "latitude", "longitude"),
                "description": _(
                    "Xaritadagi nishon <b>kenglik/uzunlik</b> bo'yicha chiziladi. "
                    "Manzilni o'zgartirsangiz, koordinata avtomatik yangilanadi: "
                    "avval xarita havolasidan olinadi, bo'lmasa manzil bo'yicha qidiriladi. "
                    "Kenglik/uzunlikni qo'lda kiritsangiz — avtomatik qidiruv o'chadi."
                ),
            },
        ),
        (_("Chop etish"), {"fields": ("order", "is_main", "is_published")}),
        translation_fieldset("name", "address", "landmark", "working_hours"),
    )

    @admin.display(description=_("Koordinata"))
    def coordinates(self, obj: Branch) -> str:
        if obj.latitude is None or obj.longitude is None:
            return str(_("— (xaritada ko'rinmaydi)"))
        return f"{obj.latitude}, {obj.longitude}"

    def save_model(self, request, obj, form, change):
        changed, note = resolve_coordinates(obj, set(form.changed_data))
        super().save_model(request, obj, form, change)
        if note:
            self.message_user(request, note, messages.SUCCESS if changed else messages.WARNING)
