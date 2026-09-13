"""DRF uchun umumiy yordamchilar: tarjima mixin'i.

Ilgari bu yerda MongoDB uchun `ObjectIdField`, `MongoJSONRenderer` va
serializer maydonlari xaritasini almashtiradigan `register_objectid_fields()`
ham bor edi. PostgreSQL'da birlamchi kalit oddiy butun son — DRF uni o'zi
to'g'ri chiqaradi, qo'shimcha hech narsa kerak emas.
"""

from .translation import DEFAULT_LANGUAGE, resolve_language


class TranslatedSerializerMixin:
    """`title_ru/_uz/_en` maydonlaridan tanlangan tildagi `title` ni qo'shadi.

    Til `?lang=uz` parametri yoki `Accept-Language` sarlavhasidan olinadi.
    """

    translated_fields: tuple[str, ...] = ()

    @property
    def language(self) -> str:
        cached = self.context.get("language")
        if cached:
            return cached
        language = resolve_language(self.context.get("request"))
        self.context["language"] = language
        return language

    def to_representation(self, instance):
        data = super().to_representation(instance)
        language = self.language if self.context else DEFAULT_LANGUAGE
        for field in self.translated_fields:
            data[field] = instance.tr(field, language)
        return data
