"""Kurslar, o'qish bosqichlari va kurs imkoniyatlari."""

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import PublishableModel, SluggedModel, TimeStampedModel
from apps.core.translation import TranslatedModel


class Direction(TranslatedModel, SluggedModel, PublishableModel):
    """Kurs yo'nalishi (IT Kids, Programmirovaniye, SPACE va h.k.)."""

    title_ru = models.CharField(_("nomi (ru)"), max_length=120)
    title_uz = models.CharField(_("nomi (uz)"), max_length=120, blank=True)
    title_en = models.CharField(_("nomi (en)"), max_length=120, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    icon = models.ImageField(_("ikonka"), upload_to="directions/", blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Yo'nalish")
        verbose_name_plural = _("Yo'nalishlar")

    def __str__(self) -> str:
        return self.title_ru


class Course(TranslatedModel, SluggedModel, PublishableModel):
    """Kurs sahifasi (masalan: «Курс / IT Kids», «Курс / Программирование»)."""

    direction = models.ForeignKey(
        Direction,
        verbose_name=_("yo'nalish"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    teachers = models.ManyToManyField(
        "teachers.Teacher",
        verbose_name=_("o'qituvchilar"),
        related_name="courses",
        blank=True,
    )

    title_ru = models.CharField(_("nomi (ru)"), max_length=160)
    title_uz = models.CharField(_("nomi (uz)"), max_length=160, blank=True)
    title_en = models.CharField(_("nomi (en)"), max_length=160, blank=True)

    subtitle_ru = models.CharField(_("qisqa izoh (ru)"), max_length=300, blank=True)
    subtitle_uz = models.CharField(_("qisqa izoh (uz)"), max_length=300, blank=True)
    subtitle_en = models.CharField(_("qisqa izoh (en)"), max_length=300, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"))
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    card_image = models.ImageField(_("karta rasmi"), upload_to="courses/", blank=True)
    hero_image = models.ImageField(_("sahifa rasmi"), upload_to="courses/", blank=True)
    accent_color = models.CharField(
        _("aksent rangi"),
        max_length=7,
        default="#E94921",
        help_text=_("HEX формат: #E94921"),
        # Qiymat saytda to'g'ridan-to'g'ri CSS rangi sifatida ishlatiladi.
        # Validatorsiz «red» yoki «E94921» (panjarasiz) kabi yozuv jimgina
        # qabul qilinardi va kurs sahifasidagi rang yo'qolib qolardi — admin
        # esa nima noto'g'ri ekanini bilmasdi.
        validators=[
            RegexValidator(
                r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$",
                message=_("Rang #RGB yoki #RRGGBB ko'rinishida bo'lishi kerak, masalan #E94921."),
            )
        ],
    )

    age_from = models.PositiveSmallIntegerField(_("yosh (dan)"), default=7)
    age_to = models.PositiveSmallIntegerField(_("yosh (gacha)"), default=17)
    duration_months = models.PositiveSmallIntegerField(_("davomiyligi (oy)"), default=9)
    lessons_per_week = models.PositiveSmallIntegerField(_("haftasiga darslar"), default=2)
    lesson_duration_minutes = models.PositiveSmallIntegerField(
        _("dars davomiyligi (daqiqa)"), default=90
    )
    price = models.DecimalField(
        _("narx (oyiga, so'm)"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    is_featured = models.BooleanField(_("bosh sahifada"), default=False, db_index=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Kurs")
        verbose_name_plural = _("Kurslar")
        indexes = [models.Index(fields=["is_published", "is_featured"])]

    def __str__(self) -> str:
        return self.title_ru

    @property
    def age_range(self) -> str:
        return f"{self.age_from}–{self.age_to}"


class CourseFeature(TranslatedModel, TimeStampedModel):
    """Kurs sahifasidagi imkoniyat/afzallik kartochkasi."""

    course = models.ForeignKey(
        Course, verbose_name=_("kurs"), on_delete=models.CASCADE, related_name="features"
    )

    title_ru = models.CharField(_("sarlavha (ru)"), max_length=200)
    title_uz = models.CharField(_("sarlavha (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("sarlavha (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    icon = models.ImageField(_("ikonka"), upload_to="courses/features/", blank=True)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Kurs imkoniyati")
        verbose_name_plural = _("Kurs imkoniyatlari")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title_ru


class CourseStage(TranslatedModel, TimeStampedModel):
    """«Этапы обучения» — o'qish bosqichlari."""

    course = models.ForeignKey(
        Course, verbose_name=_("kurs"), on_delete=models.CASCADE, related_name="stages"
    )
    number = models.CharField(_("raqam"), max_length=4, blank=True)

    title_ru = models.CharField(_("bosqich nomi (ru)"), max_length=200)
    title_uz = models.CharField(_("bosqich nomi (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("bosqich nomi (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    image = models.ImageField(_("rasm"), upload_to="courses/stages/", blank=True)
    duration_months = models.PositiveSmallIntegerField(_("davomiyligi (oy)"), default=0)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("O'qish bosqichi")
        verbose_name_plural = _("O'qish bosqichlari")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.course.title_ru} — {self.title_ru}"


class CourseFaq(TranslatedModel, TimeStampedModel):
    """Kurs sahifasining pastidagi «Частые вопросы» bloki.

    Har bir kursning savollari o'ziniki, shuning uchun ular admin panelda
    kursning o'z sahifasi ichida — bosqichlar va imkoniyatlar bilan yonma-yon —
    tahrirlanadi. Bosh sahifadagi umumiy FAQ esa alohida (`core.FAQ`) qoladi.
    """

    course = models.ForeignKey(
        Course, verbose_name=_("kurs"), on_delete=models.CASCADE, related_name="faqs"
    )

    question_ru = models.CharField(_("savol (ru)"), max_length=255)
    question_uz = models.CharField(_("savol (uz)"), max_length=255, blank=True)
    question_en = models.CharField(_("savol (en)"), max_length=255, blank=True)

    answer_ru = models.TextField(_("javob (ru)"))
    answer_uz = models.TextField(_("javob (uz)"), blank=True)
    answer_en = models.TextField(_("javob (en)"), blank=True)

    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Savol-javob")
        verbose_name_plural = _("Savol-javoblar")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.question_ru
