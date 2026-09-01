from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "apps.core"
    verbose_name = "Umumiy"

    def ready(self) -> None:
        # DRF ObjectId maydonlarini satr sifatida chiqarishi uchun ro'yxatdan o'tkazamiz.
        from .drf import register_objectid_fields

        register_objectid_fields()
        self._tune_admin_defaults()

    @staticmethod
    def _tune_admin_defaults() -> None:
        """Barcha admin ro'yxatlari uchun MongoDB'ga mos standartlar.

        MongoDB Atlas Railway'dan tashqarida turgani uchun har bir so'rov ~150 ms
        turadi. Django admin esa ro'yxat sahifasida ortiqcha ish qiladi:

        * `show_full_result_count` — sahifalash uchun bitta `count()` yetarli
          bo'lsa ham, Django "N natijadan M tasi" yozuvi uchun **ikkinchi**,
          filtrsiz `count()` yuboradi. Bu yozuv kerak emas, so'rov esa qimmat.
        * `list_per_page` standart 100 ta — har bir sahifada 100 hujjat o'qiladi.
          Kontent hajmi kichik, 25 ta yetarli va sezilarli darajada tez.

        Har bir `ModelAdmin` da qo'lda takrorlamaslik uchun standart qiymatlar
        bir joyda o'zgartiriladi (django-axes va auth admin'lariga ham tegishli).
        """
        from django.contrib import admin

        admin.ModelAdmin.show_full_result_count = False
        admin.ModelAdmin.list_per_page = 25
        admin.ModelAdmin.list_max_show_all = 200
