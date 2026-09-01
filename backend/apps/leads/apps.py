from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.leads"
    verbose_name = "Arizalar"
