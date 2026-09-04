"""«Контакты / Филиалы / Карта» sahifasi modellari."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import PublishableModel, SluggedModel, TimeStampedModel
from apps.core.translation import TranslatedModel


class Branch(TranslatedModel, SluggedModel, PublishableModel):
    name_ru = models.CharField(_("nomi (ru)"), max_length=160)
    name_uz = models.CharField(_("nomi (uz)"), max_length=160, blank=True)
    name_en = models.CharField(_("nomi (en)"), max_length=160, blank=True)

    address_ru = models.CharField(_("manzil (ru)"), max_length=255)
    address_uz = models.CharField(_("manzil (uz)"), max_length=255, blank=True)
    address_en = models.CharField(_("manzil (en)"), max_length=255, blank=True)

    landmark_ru = models.CharField(_("mo'ljal (ru)"), max_length=255, blank=True)
    landmark_uz = models.CharField(_("mo'ljal (uz)"), max_length=255, blank=True)
    landmark_en = models.CharField(_("mo'ljal (en)"), max_length=255, blank=True)

    working_hours_ru = models.CharField(_("ish vaqti (ru)"), max_length=160, blank=True)
    working_hours_uz = models.CharField(_("ish vaqti (uz)"), max_length=160, blank=True)
    working_hours_en = models.CharField(_("ish vaqti (en)"), max_length=160, blank=True)
    phone = models.CharField(_("telefon"), max_length=32, blank=True)

    # Koordinata chegaradan chiqsa xarita nishoni okean o'rtasida paydo
    # bo'lardi va buni faqat sayt ochilganda sezish mumkin edi. Validator
    # xatoni admin panelning o'zida ushlaydi.
    latitude = models.FloatField(
        _("kenglik (latitude)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text=_(
            "Xaritadagi nishon shu koordinatada turadi. "
            "Bo'sh qoldirsangiz — havoladan yoki manzildan avtomatik topiladi."
        ),
    )
    longitude = models.FloatField(
        _("uzunlik (longitude)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    map_url_yandex = models.URLField(
        _("Yandex Maps havolasi"),
        blank=True,
        help_text=_("Masalan: https://yandex.uz/maps/?ll=69.240562,41.311081&z=17"),
    )
    map_url_google = models.URLField(
        _("Google Maps havolasi"),
        blank=True,
        help_text=_("Masalan: https://www.google.com/maps/@41.311081,69.240562,17z"),
    )

    cover = models.ImageField(_("asosiy rasm"), upload_to="branches/", blank=True)
    is_main = models.BooleanField(_("bosh filial"), default=False)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Filial")
        verbose_name_plural = _("Filiallar")

    def __str__(self) -> str:
        return self.name_ru

    def _slug_source(self) -> str:
        return self.name_ru


class BranchImage(TimeStampedModel):
    """Filial galereyasi."""

    branch = models.ForeignKey(
        Branch, verbose_name=_("filial"), on_delete=models.CASCADE, related_name="gallery"
    )
    image = models.ImageField(_("rasm"), upload_to="branches/gallery/")
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Filial rasmi")
        verbose_name_plural = _("Filial rasmlari")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.branch.name_ru} — {self.order}"
