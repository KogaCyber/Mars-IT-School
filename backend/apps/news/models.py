"""«Новости» va «Новость / Галерея» sahifalari modellari."""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import PublishableModel, SluggedModel, TimeStampedModel
from apps.core.translation import TranslatedModel


class NewsCategory(TranslatedModel, SluggedModel, PublishableModel):
    title_ru = models.CharField(_("nomi (ru)"), max_length=80)
    title_uz = models.CharField(_("nomi (uz)"), max_length=80, blank=True)
    title_en = models.CharField(_("nomi (en)"), max_length=80, blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Yangilik turkumi")
        verbose_name_plural = _("Yangilik turkumlari")

    def __str__(self) -> str:
        return self.title_ru


class News(TranslatedModel, SluggedModel, PublishableModel):
    """Yangilik/maqola. Bosh sahifadagi «Что происходит в школе» bloki ham shundan."""

    category = models.ForeignKey(
        NewsCategory,
        verbose_name=_("turkum"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news",
    )

    title_ru = models.CharField(_("sarlavha (ru)"), max_length=200)
    title_uz = models.CharField(_("sarlavha (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("sarlavha (en)"), max_length=200, blank=True)

    excerpt_ru = models.CharField(_("qisqa matn (ru)"), max_length=400)
    excerpt_uz = models.CharField(_("qisqa matn (uz)"), max_length=400, blank=True)
    excerpt_en = models.CharField(_("qisqa matn (en)"), max_length=400, blank=True)

    body_ru = models.TextField(_("matn (ru)"))
    body_uz = models.TextField(_("matn (uz)"), blank=True)
    body_en = models.TextField(_("matn (en)"), blank=True)

    cover = models.ImageField(_("muqova"), upload_to="news/")
    published_at = models.DateTimeField(_("chop etilgan vaqt"), default=timezone.now, db_index=True)
    reading_minutes = models.PositiveSmallIntegerField(_("o'qish vaqti (daq.)"), default=3)
    views_count = models.PositiveIntegerField(_("ko'rishlar"), default=0, editable=False)
    is_featured = models.BooleanField(_("bosh sahifada"), default=False, db_index=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Yangilik")
        verbose_name_plural = _("Yangiliklar")
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title_ru


class NewsImage(TranslatedModel, TimeStampedModel):
    """«Новость / Галерея» — yangilikka biriktirilgan rasmlar."""

    news = models.ForeignKey(
        News, verbose_name=_("yangilik"), on_delete=models.CASCADE, related_name="gallery"
    )
    image = models.ImageField(_("rasm"), upload_to="news/gallery/")
    caption_ru = models.CharField(_("izoh (ru)"), max_length=200, blank=True)
    caption_uz = models.CharField(_("izoh (uz)"), max_length=200, blank=True)
    caption_en = models.CharField(_("izoh (en)"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Galereya rasmi")
        verbose_name_plural = _("Galereya rasmlari")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.news.title_ru} — {self.order}"
