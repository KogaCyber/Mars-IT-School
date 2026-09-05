"""Sahifa bo'limlari uchun admin panel.

Har bir sahifa uchun alohida ro'yxat: «Bosh sahifa bo'limlari», «IT Kids
sahifasi bo'limlari»… Ro'yxatdagi tartib — saytdagi tartib (yuqoridan pastga),
shuning uchun kontent kirituvchi odam sahifani ko'z oldiga keltirib ishlaydi.

Bo'limni ochganda faqat o'sha blokka tegishli maydonlar ko'rinadi: reestrda
(`sections.py`) sanab o'tilganlari. Masalan galereyada — sarlavha, izoh va
rasmlar; hero blokida — sarlavha, matn, tugmalar va rasm.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import SECTION_PROXIES, PageSection, SectionItem
from .section_sync import sync_quietly
from .sections import PAGE_URLS, SECTION_INDEX
from .translation import CONTENT_LANGUAGES, DEFAULT_LANGUAGE

#: Tarjima qilinadigan maydonlar (asosi → uchta til maydoni).
TRANSLATED_BASES = frozenset(
    {"eyebrow", "title", "subtitle", "text", "note", "button_label", "button2_label"}
)
TRANSLATED_ITEM_BASES = frozenset({"value", "label", "title", "text", "note", "list"})


def _expand(fields, translated_bases, language):
    """Maydon asoslarini shu tildagi haqiqiy maydon nomlariga aylantiradi."""
    result = []
    for base in fields:
        if base in translated_bases:
            result.append(f"{base}_{language}")
        elif language == DEFAULT_LANGUAGE:
            # Tarjimasiz maydon (rasm, havola) faqat bir marta — asosiy blokda.
            result.append(base)
    return result


class SectionItemInline(admin.StackedInline):
    """Bo'lim ichidagi kartochkalar/bosqichlar/rasmlar."""

    model = SectionItem
    extra = 0
    ordering = ("order",)

    def get_fields(self, request, obj=None):
        spec = SECTION_INDEX.get(getattr(obj, "key", ""), {})
        item_fields = spec.get("items", ())
        fields = ["order", *_expand(item_fields, TRANSLATED_ITEM_BASES, DEFAULT_LANGUAGE)]
        for language in CONTENT_LANGUAGES:
            if language == DEFAULT_LANGUAGE:
                continue
            fields += _expand(item_fields, TRANSLATED_ITEM_BASES, language)
        fields.append("is_published")
        return fields

    def get_formset(self, request, obj=None, **kwargs):
        spec = SECTION_INDEX.get(getattr(obj, "key", ""), {})
        self.verbose_name = spec.get("item_name", _("Element"))
        self.verbose_name_plural = spec.get("item_name", _("Elementlar"))
        return super().get_formset(request, obj, **kwargs)


class PageSectionAdmin(admin.ModelAdmin):
    """Bitta sahifaning bo'limlari. Proksi-modellar shundan meros oladi."""

    #: Proksi-model qaysi sahifani ko'rsatishi (`models.py` da belgilanadi).
    page_slug = ""

    list_display = ("section_name", "section_hint", "visible")
    list_display_links = ("section_name",)
    readonly_fields = ("section_help",)
    inlines = [SectionItemInline]
    save_on_top = True

    # Bo'limlar ro'yxati reestrdan keladi — qo'lda qo'shish/o'chirish yo'q.
    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        page = self.page_slug or getattr(self.model, "page_slug", "")
        return queryset.filter(page=page) if page else queryset

    def changelist_view(self, request, extra_context=None):
        # Yangi bo'lim reestrga qo'shilgan bo'lsa, ro'yxatda darrov ko'rinsin.
        sync_quietly()
        return super().changelist_view(request, extra_context=extra_context)

    # -------------------------- ro'yxat ustunlari --------------------------
    @admin.display(description=_("Bo'lim"), ordering="order")
    def section_name(self, obj) -> str:
        spec = SECTION_INDEX.get(obj.key)
        return str(spec["name"]) if spec else obj.key

    @admin.display(description=_("Nimani o'zgartirish mumkin"))
    def section_hint(self, obj) -> str:
        spec = SECTION_INDEX.get(obj.key)
        return str(spec["hint"]) if spec else ""

    @admin.display(description=_("saytda ko'rsatilsin"), boolean=True)
    def visible(self, obj) -> bool:
        # Yashirib bo'lmaydigan bo'lim ro'yxatda ham doim «ko'rinadi».
        spec = SECTION_INDEX.get(obj.key, {})
        return obj.is_published if spec.get("hideable", True) else True

    # ------------------------------ shakl ----------------------------------
    @admin.display(description=_("Bu blok saytda qayerda"))
    def section_help(self, obj) -> str:
        spec = SECTION_INDEX.get(getattr(obj, "key", ""), {})
        url = PAGE_URLS.get(getattr(obj, "page", ""), "")
        return format_html(
            "<div style='line-height:1.6'><b>{}</b><br>{}{}</div>",
            spec.get("name", ""),
            spec.get("hint", ""),
            format_html("<br>Sahifa: <code>{}</code>", url) if url else "",
        )

    def get_fieldsets(self, request, obj=None):
        spec = SECTION_INDEX.get(getattr(obj, "key", ""), {})
        fields = spec.get("fields", ())

        main = _expand(fields, TRANSLATED_BASES, DEFAULT_LANGUAGE)
        # Yashirib bo'lmaydigan bo'limda («Umumiy tugmalar», test qadamlari,
        # podval) belgi ko'rsatilmaydi — u alohida blok emas, sayt matni.
        toggle = ("is_published",) if spec.get("hideable", True) else ()
        fieldsets = [
            (None, {"fields": ("section_help", *main, *toggle)}),
        ]

        for language in CONTENT_LANGUAGES:
            if language == DEFAULT_LANGUAGE:
                continue
            translated = _expand(fields, TRANSLATED_BASES, language)
            if translated:
                fieldsets.append(
                    (
                        _("Tarjima — %(lang)s") % {"lang": language.upper()},
                        {"fields": tuple(translated), "classes": ("collapse",)},
                    )
                )

        return fieldsets

    def get_inline_instances(self, request, obj=None):
        # Elementlari yo'q bo'limda bo'sh «Elementlar» bloki ko'rinmasin.
        spec = SECTION_INDEX.get(getattr(obj, "key", ""), {})
        if not spec.get("items"):
            return []
        return super().get_inline_instances(request, obj)


def register_section_admins(site) -> None:
    """Har bir sahifa uchun proksi-modelni admin panelga qo'shadi."""
    for page_slug, model in SECTION_PROXIES.items():
        admin_class = type(
            f"{model.__name__}Admin",
            (PageSectionAdmin,),
            {"page_slug": page_slug},
        )
        site.register(model, admin_class)

    # Asosiy model menyuda ko'rinmaydi — u faqat sahifalar orqali tahrirlanadi.
    if PageSection in site._registry:
        site.unregister(PageSection)
