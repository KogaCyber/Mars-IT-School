from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.core"
    verbose_name = "Umumiy"

    def ready(self) -> None:
        # DRF ObjectId maydonlarini satr sifatida chiqarishi uchun ro'yxatdan o'tkazamiz.
        from .drf import register_objectid_fields

        register_objectid_fields()
