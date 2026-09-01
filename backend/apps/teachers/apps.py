from django.apps import AppConfig


class TeachersConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.teachers"
    verbose_name = "O'qituvchilar"
