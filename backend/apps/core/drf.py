"""DRF ↔ MongoDB integratsiyasi: ObjectId maydonlari va tarjima mixin'i."""

from bson import ObjectId
from bson.errors import InvalidId
from django_mongodb_backend.fields import ObjectIdAutoField
from django_mongodb_backend.fields import ObjectIdField as MongoObjectIdField
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder

from .translation import DEFAULT_LANGUAGE, resolve_language


@extend_schema_field(OpenApiTypes.STR)
class ObjectIdField(serializers.Field):
    """MongoDB `_id` maydonini JSON'da satr sifatida beradi va qabul qiladi."""

    default_error_messages = {"invalid": "Noto'g'ri identifikator."}

    def to_representation(self, value) -> str:
        return str(value)

    def to_internal_value(self, data) -> ObjectId:
        try:
            return ObjectId(str(data))
        except (InvalidId, TypeError):
            self.fail("invalid")


class MongoJSONEncoder(JSONEncoder):
    """ObjectId qiymatini JSON'ga yozishda satrga aylantiradi."""

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


class MongoJSONRenderer(JSONRenderer):
    encoder_class = MongoJSONEncoder


def register_objectid_fields() -> None:
    """ModelSerializer avtomatik ravishda ObjectId maydonlarini to'g'ri chiqarishi uchun."""
    mapping = serializers.ModelSerializer.serializer_field_mapping
    mapping[ObjectIdAutoField] = ObjectIdField
    mapping[MongoObjectIdField] = ObjectIdField


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
