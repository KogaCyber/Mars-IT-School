from django.apps import AppConfig


class QuizConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.quiz"
    verbose_name = "Testlar"
