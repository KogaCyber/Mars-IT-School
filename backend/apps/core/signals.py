"""Kontent o'zgarganda saytga xabar beruvchi signallar.

Har bir modelga alohida ulanmaymiz: kontent ilovalari ro'yxati bo'yicha
filtrlaydigan bitta qabul qiluvchi yetarli — yangi model qo'shilganda hech
narsani unutib qoldirish xavfi yo'q.

Ariza/anketa kabi foydalanuvchi yuboradigan yozuvlar ro'yxatdan chiqarilgan:
ular saytdagi kontentni o'zgartirmaydi, versiyani ko'tarsa esa barcha
tashrifchilar kontentni bekorga qayta yuklardi (arizalar admin panelda
baribir darhol ko'rinadi — u yerda kesh yo'q).
"""

import logging

from django.db.models.signals import post_delete, post_save

from .revision import bump_revision

logger = logging.getLogger(__name__)

#: Saytda ko'rinadigan kontentga ega ilovalar.
CONTENT_APPS = frozenset({"core", "courses", "teachers", "news", "branches", "vacancies", "quiz"})

#: Kontent hisoblanmaydigan (yoki versiyaning o'zi bo'lgan) modellar.
IGNORED_MODELS = frozenset({"core.SiteRevision", "quiz.Submission", "vacancies.VacancyApplication"})


def _on_content_change(sender, **kwargs) -> None:
    meta = getattr(sender, "_meta", None)
    if meta is None or meta.app_label not in CONTENT_APPS:
        return
    if meta.label in IGNORED_MODELS:
        return

    try:
        bump_revision()
    except Exception:  # noqa: BLE001 — saqlash signal xatosi tufayli buzilmasin
        logger.exception("Kontent versiyasini yangilab bo'lmadi (%s)", meta.label)


def connect() -> None:
    post_save.connect(_on_content_change, dispatch_uid="core.revision.post_save")
    post_delete.connect(_on_content_change, dispatch_uid="core.revision.post_delete")
