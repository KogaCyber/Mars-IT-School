"""Django va uchinchi tomon ilovalarini MongoDB uchun moslashtirish.

Bu ilovalar o'z AppConfig'ida `AutoField` ni birlamchi kalit sifatida belgilaydi,
MongoDB esa `ObjectIdAutoField` talab qiladi. Shu sababli ularning
konfiguratsiyasidan meros olib, faqat shu sozlama qayta belgilanadi.
"""

from axes.apps import AppConfig as AxesAppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig

OBJECT_ID_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAdminConfig(AdminConfig):
    default_auto_field = OBJECT_ID_FIELD


class MongoAuthConfig(AuthConfig):
    default_auto_field = OBJECT_ID_FIELD


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = OBJECT_ID_FIELD


class MongoAxesConfig(AxesAppConfig):
    default_auto_field = OBJECT_ID_FIELD
