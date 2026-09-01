"""«Преподаватели, которые работают в IT» bo'limi modellari."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import PublishableModel, SluggedModel
from apps.core.translation import TranslatedModel


class Skill(models.Model):
    """Texnologiya belgisi (HTML, CSS, JavaScript, React va h.k.)."""

    name = models.CharField(_("nomi"), max_length=60, unique=True)
    icon = models.ImageField(_("ikonka"), upload_to="skills/", blank=True)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Texnologiya")
        verbose_name_plural = _("Texnologiyalar")
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class Teacher(TranslatedModel, SluggedModel, PublishableModel):
    full_name = models.CharField(_("ism familiya"), max_length=120)
    photo = models.ImageField(_("rasm"), upload_to="teachers/", blank=True)

    position_ru = models.CharField(_("lavozim (ru)"), max_length=160)
    position_uz = models.CharField(_("lavozim (uz)"), max_length=160, blank=True)
    position_en = models.CharField(_("lavozim (en)"), max_length=160, blank=True)

    # Kartochka o'ng yuqorisidagi yorliq (masalan: «Back-End»)
    badge = models.CharField(_("yorliq"), max_length=40, blank=True)

    bio_ru = models.TextField(_("mutaxassisligi (ru)"), blank=True)
    bio_uz = models.TextField(_("mutaxassisligi (uz)"), blank=True)
    bio_en = models.TextField(_("mutaxassisligi (en)"), blank=True)

    company = models.CharField(_("ish joyi"), max_length=120, blank=True)
    company_logo = models.ImageField(_("kompaniya logosi"), upload_to="teachers/logos/", blank=True)
    experience_years = models.PositiveSmallIntegerField(_("tajriba (yil)"), default=0)
    students_count = models.PositiveIntegerField(_("o'quvchilar soni"), default=0)

    skills = models.ManyToManyField(
        Skill, verbose_name=_("texnologiyalar"), related_name="teachers", blank=True
    )

    telegram_url = models.URLField(_("Telegram"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("O'qituvchi")
        verbose_name_plural = _("O'qituvchilar")

    def __str__(self) -> str:
        return self.full_name

    def _slug_source(self) -> str:
        return self.full_name
