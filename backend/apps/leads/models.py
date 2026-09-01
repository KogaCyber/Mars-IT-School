"""Saytdagi barcha formalardan keladigan arizalar («Заявка»)."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_uz_phone
from apps.core.models import TimeStampedModel


class Lead(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", _("Yangi")
        IN_PROGRESS = "in_progress", _("Bog'lanildi")
        ENROLLED = "enrolled", _("Ro'yxatdan o'tdi")
        REJECTED = "rejected", _("Rad etildi")

    class Source(models.TextChoices):
        HOME = "home", _("Bosh sahifa")
        COURSE = "course", _("Kurs sahifasi")
        COURSES = "courses", _("Kurslar sahifasi")
        SPACE = "space", _("SPACE sahifasi")
        QUIZ = "quiz", _("Test natijasi")
        CONTACTS = "contacts", _("Kontaktlar sahifasi")
        POPUP = "popup", _("Popup forma")

    full_name = models.CharField(_("ism familiya"), max_length=120)
    phone = models.CharField(_("telefon"), max_length=13, validators=[validate_uz_phone])
    course = models.ForeignKey(
        "courses.Course",
        verbose_name=_("kurs"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        verbose_name=_("filial"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    child_age = models.PositiveSmallIntegerField(_("bola yoshi"), null=True, blank=True)
    comment = models.TextField(_("izoh"), max_length=1000, blank=True)
    source = models.CharField(
        _("manba"), max_length=16, choices=Source.choices, default=Source.HOME
    )
    status = models.CharField(
        _("holat"), max_length=16, choices=Status.choices, default=Status.NEW, db_index=True
    )
    admin_note = models.TextField(_("admin izohi"), blank=True)

    # Spam tahlili uchun texnik ma'lumot (foydalanuvchiga qaytarilmaydi).
    ip_address = models.GenericIPAddressField(_("IP manzil"), null=True, blank=True)
    user_agent = models.CharField(_("User-Agent"), max_length=300, blank=True)

    class Meta:
        verbose_name = _("Ariza")
        verbose_name_plural = _("Arizalar")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.full_name} — {self.phone}"
