from django.contrib import admin

from apps.core.translation import translation_fieldset

from .models import News, NewsCategory, NewsImage


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ("order", "image", "caption_ru", "caption_uz", "caption_en")


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "order", "is_published")
    list_editable = ("order", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "order", "is_published")}),
        translation_fieldset("title"),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "category", "published_at", "views_count", "is_published")
    list_filter = ("category", "is_published", "is_featured")
    list_select_related = ("category",)
    search_fields = ("title_ru", "excerpt_ru", "body_ru")
    date_hierarchy = "published_at"
    readonly_fields = ("views_count",)
    inlines = [NewsImageInline]
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "category", "excerpt_ru", "body_ru", "cover")}),
        (
            "Chop etish",
            {
                "fields": (
                    "published_at",
                    "reading_minutes",
                    "is_featured",
                    "is_published",
                    "order",
                    "views_count",
                )
            },
        ),
        translation_fieldset("title", "excerpt", "body"),
    )
