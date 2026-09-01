from django.apps import AppConfig


class BranchesConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.branches"
    verbose_name = "Filiallar"
