"""«Вакансии» va «Вакансия / Заявка» sahifalari modellari."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_uz_phone
from apps.core.models import PublishableModel, SluggedModel, TimeStampedModel
from apps.core.translation import TranslatedModel


class Vacancy(TranslatedModel, SluggedModel, PublishableModel):
    class Icon(models.TextChoices):
        """Kartochkaning pastki burchagidagi chiziqli ikonka."""

        CAP = "cap", _("Bitiruvchi shapkasi (o'qituvchi)")
        BADGE = "badge", _("Nishon (administrator)")
        USERS = "users", _("Jamoa (kurator)")
        HEADSET = "headset", _("Naushnik (kol-markaz)")
        SPARK = "spark", _("Uchqun (boshqa)")

    class Employment(models.TextChoices):
        FULL_TIME = "full_time", _("To'liq stavka")
        PART_TIME = "part_time", _("Yarim stavka")
        PROJECT = "project", _("Loyiha asosida")

    branch = models.ForeignKey(
        "branches.Branch",
        verbose_name=_("filial"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacancies",
    )

    title_ru = models.CharField(_("lavozim (ru)"), max_length=160)
    title_uz = models.CharField(_("lavozim (uz)"), max_length=160, blank=True)
    title_en = models.CharField(_("lavozim (en)"), max_length=160, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"))
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    requirements_ru = models.TextField(_("talablar (ru)"), blank=True)
    requirements_uz = models.TextField(_("talablar (uz)"), blank=True)
    requirements_en = models.TextField(_("talablar (en)"), blank=True)

    conditions_ru = models.TextField(_("shartlar (ru)"), blank=True)
    conditions_uz = models.TextField(_("shartlar (uz)"), blank=True)
    conditions_en = models.TextField(_("shartlar (en)"), blank=True)

    employment_type = models.CharField(
        _("bandlik turi"),
        max_length=16,
        choices=Employment.choices,
        default=Employment.FULL_TIME,
    )
    icon_name = models.CharField(
        _("ikonka"), max_length=16, choices=Icon.choices, default=Icon.SPARK
    )
    salary_from = models.PositiveIntegerField(_("maosh (dan)"), null=True, blank=True)
    salary_to = models.PositiveIntegerField(_("maosh (gacha)"), null=True, blank=True)
    is_open = models.BooleanField(_("ochiq"), default=True, db_index=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Vakansiya")
        verbose_name_plural = _("Vakansiyalar")

    def __str__(self) -> str:
        return self.title_ru


class VacancyApplication(TimeStampedModel):
    """Vakansiyaga yuborilgan ariza."""

    class Status(models.TextChoices):
        NEW = "new", _("Yangi")
        REVIEWED = "reviewed", _("Ko'rib chiqildi")
        INVITED = "invited", _("Suhbatga taklif qilindi")
        REJECTED = "rejected", _("Rad etildi")

    vacancy = models.ForeignKey(
        Vacancy,
        verbose_name=_("vakansiya"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="applications",
    )
    full_name = models.CharField(_("ism familiya"), max_length=120)
    phone = models.CharField(_("telefon"), max_length=13, validators=[validate_uz_phone])
    email = models.EmailField(_("email"), blank=True)
    cover_letter = models.TextField(_("xat"), max_length=2000, blank=True)
    resume = models.FileField(_("rezyume"), upload_to="resumes/%Y/%m/", blank=True)
    resume_url = models.URLField(_("rezyume havolasi"), max_length=500, blank=True)
    status = models.CharField(
        _("holat"), max_length=16, choices=Status.choices, default=Status.NEW, db_index=True
    )

    ip_address = models.GenericIPAddressField(_("IP manzil"), null=True, blank=True)

    class Meta:
        verbose_name = _("Vakansiya arizasi")
        verbose_name_plural = _("Vakansiya arizalari")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} — {self.vacancy_id}"
