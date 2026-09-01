from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "course", "source", "status", "created_at")
    list_filter = ("status", "source", "created_at", "course")
    search_fields = ("full_name", "phone", "comment")
    list_select_related = ("course", "branch")
    date_hierarchy = "created_at"
    readonly_fields = (
        "full_name", "phone", "course", "branch", "child_age", "comment", "source",
        "ip_address", "user_agent", "created_at", "updated_at",
    )
    fields = readonly_fields + ("status", "admin_note")

    def has_add_permission(self, request) -> bool:
        # Arizalar faqat sayt orqali kiradi.
        return False
