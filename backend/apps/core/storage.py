"""Shaxsiy (ommaga ochilmaydigan) fayllar uchun saqlagich.

`MEDIA_ROOT` ni WhiteNoise butunlay ochiq uzatadi (`config/wsgi.py`) — bu sayt
rasmlari uchun to'g'ri, lekin nomzodning rezyumesi shaxsiy ma'lumot. U yerga
tushgan fayl manzilini taxmin qilgan har qanday odam uni yuklab olardi
(`/media/resumes/2026/09/ivanov_cv.pdf`).

Shu sababli bunday fayllar `PRIVATE_MEDIA_ROOT` ichida — hech qaysi statik
uzatuvchi ko'rmaydigan papkada — saqlanadi va faqat
`apps.vacancies.views.resume_download_view` orqali, xodim huquqi bilan
beriladi.

Saqlagich CHAQIRILUVCHI (callable) sifatida uzatiladi: shunda Django uni
migratsiya ichiga yozib qo'ymaydi va papka manzilini muhitga qarab
o'zgartirish mumkin bo'ladi.
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateMediaStorage(FileSystemStorage):
    """`PRIVATE_MEDIA_ROOT` ichiga yozadi va hech qanday ommaviy URL bermaydi."""

    def __init__(self, **kwargs):
        kwargs.setdefault("location", str(settings.PRIVATE_MEDIA_ROOT))
        kwargs.setdefault("base_url", None)
        super().__init__(**kwargs)

    def url(self, name):
        """Ommaviy havola YO'Q — chaqirilsa darhol xatolik.

        `base_url=None` yetarli emas: `FileSystemStorage` bunda jimgina
        `MEDIA_URL` ga qaytadi va `/media/resumes/...` kabi manzil yasab
        berardi. Bu aynan biz yopmoqchi bo'lgan manzil ko'rinishi — shablon
        yoki serializer tasodifan uni chiqarib yuborsa, muammo sezilmay
        qolardi. Shuning uchun jimgina qaytish o'rniga ochiq xatolik.
        """
        raise ValueError(
            "Rezyume fayllarining ommaviy havolasi yo'q. "
            "Yuklab olish uchun `resume-download` manzilidan foydalaning."
        )


def private_storage() -> PrivateMediaStorage:
    """Model maydonlari uchun chaqiriluvchi saqlagich."""
    return PrivateMediaStorage()
