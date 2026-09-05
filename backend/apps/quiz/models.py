"""«Тест» va «Результаты теста» sahifalari — proforientatsiya testi."""

import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_uz_phone
from apps.core.models import PublishableModel, SluggedModel, TimeStampedModel
from apps.core.translation import DEFAULT_LANGUAGE, TranslatedModel


class Quiz(TranslatedModel, SluggedModel, PublishableModel):
    title_ru = models.CharField(_("nomi (ru)"), max_length=200)
    title_uz = models.CharField(_("nomi (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("nomi (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    questions_per_attempt = models.PositiveSmallIntegerField(
        _("bir urinishdagi savollar soni"),
        default=20,
        help_text=_(
            "Savollar bazasidan har safar shuncha savol tasodifiy tanlanadi. "
            "0 — barcha savollar ko'rsatiladi."
        ),
    )

    class Meta(PublishableModel.Meta):
        verbose_name = _("Test")
        verbose_name_plural = _("Testlar")

    def __str__(self) -> str:
        return self.title_ru


class Question(TranslatedModel, TimeStampedModel):
    quiz = models.ForeignKey(
        Quiz, verbose_name=_("test"), on_delete=models.CASCADE, related_name="questions"
    )

    text_ru = models.CharField(_("savol (ru)"), max_length=300)
    text_uz = models.CharField(_("savol (uz)"), max_length=300, blank=True)
    text_en = models.CharField(_("savol (en)"), max_length=300, blank=True)

    image = models.ImageField(_("rasm"), upload_to="quiz/", blank=True)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Savol")
        verbose_name_plural = _("Savollar")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.text_ru


class Outcome(TranslatedModel, TimeStampedModel):
    """Test natijasi (masalan: «Тебе подойдёт направление Программирование»)."""

    quiz = models.ForeignKey(
        Quiz, verbose_name=_("test"), on_delete=models.CASCADE, related_name="outcomes"
    )
    courses = models.ManyToManyField(
        "courses.Course", verbose_name=_("tavsiya qilinadigan kurslar"), blank=True
    )

    title_ru = models.CharField(_("natija (ru)"), max_length=200)
    title_uz = models.CharField(_("natija (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("natija (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    image = models.ImageField(_("rasm"), upload_to="quiz/outcomes/", blank=True)
    code = models.SlugField(_("kod"), max_length=60, help_text=_("Javoblardagi kod bilan bir xil"))

    class Meta:
        verbose_name = _("Test natijasi")
        verbose_name_plural = _("Test natijalari")
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title_ru


class Skill(models.TextChoices):
    """Test o'lchaydigan ko'nikmalar — natija sahifasidagi «Qobiliyatlar tahlili».

    Yorliqlar admin panel uchun (asosiy til). Saytga chiqadigan nom
    `SKILL_LABELS` dan tanlangan tilda olinadi — `skill_label()` ga qarang.
    """

    LOGIC = "logic", "Логическое мышление"
    MATH = "math", "Математическое мышление"
    ACCURACY = "accuracy", "Точность и порядок"
    PATIENCE = "patience", "Терпение"
    CREATIVITY = "creativity", "Креативность"
    VISUAL = "visual", "Визуальное восприятие"
    COMMUNICATION = "communication", "Коммуникабельность"
    SOCIAL = "social", "Социальная активность"


#: Ko'nikma nomlari uch tilda — natija sahifasidagi diagramma shulardan yig'iladi.
SKILL_LABELS: dict[str, dict[str, str]] = {
    Skill.LOGIC: {
        "ru": "Логическое мышление",
        "uz": "Mantiqiy tafakkur",
        "en": "Logical thinking",
    },
    Skill.MATH: {
        "ru": "Математическое мышление",
        "uz": "Matematik tafakkur",
        "en": "Mathematical thinking",
    },
    Skill.ACCURACY: {
        "ru": "Точность и порядок",
        "uz": "Aniqlik va tartib",
        "en": "Precision and order",
    },
    Skill.PATIENCE: {
        "ru": "Терпение",
        "uz": "Sabr",
        "en": "Patience",
    },
    Skill.CREATIVITY: {
        "ru": "Креативность",
        "uz": "Ijodkorlik",
        "en": "Creativity",
    },
    Skill.VISUAL: {
        "ru": "Визуальное восприятие",
        "uz": "Vizual idrok",
        "en": "Visual perception",
    },
    Skill.COMMUNICATION: {
        "ru": "Коммуникабельность",
        "uz": "Muloqotchanlik",
        "en": "Communication",
    },
    Skill.SOCIAL: {
        "ru": "Социальная активность",
        "uz": "Ijtimoiy faollik",
        "en": "Social activity",
    },
}


def skill_label(code: str, language: str) -> str:
    """Ko'nikma nomini tanlangan tilda beradi (topilmasa — asosiy til)."""
    names = SKILL_LABELS.get(code)
    if not names:
        return code
    return names.get(language) or names[DEFAULT_LANGUAGE]


class Option(TranslatedModel, TimeStampedModel):
    """Savolning javob varianti.

    Har bir variant bitta natijaga (`outcome`) ball qo'shadi va bitta
    ko'nikmani (`skill`) namoyish qiladi — ko'nikmalar natija sahifasidagi
    tahlil diagrammasini yig'ish uchun ishlatiladi.
    """

    question = models.ForeignKey(
        Question, verbose_name=_("savol"), on_delete=models.CASCADE, related_name="options"
    )
    outcome = models.ForeignKey(
        Outcome,
        verbose_name=_("natija"),
        on_delete=models.CASCADE,
        related_name="options",
        null=True,
        blank=True,
    )

    text_ru = models.CharField(_("javob (ru)"), max_length=300)
    text_uz = models.CharField(_("javob (uz)"), max_length=300, blank=True)
    text_en = models.CharField(_("javob (en)"), max_length=300, blank=True)

    skill = models.CharField(
        _("ko'nikma"),
        max_length=32,
        choices=Skill.choices,
        blank=True,
        help_text=_("Shu javob qaysi ko'nikmani ko'rsatadi (natija tahlili uchun)."),
    )

    weight = models.PositiveSmallIntegerField(_("ball"), default=1)
    order = models.PositiveIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name = _("Javob varianti")
        verbose_name_plural = _("Javob variantlari")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.text_ru


def new_public_token() -> str:
    """Natija havolasi uchun taxmin qilib bo'lmaydigan identifikator (256 bit)."""
    return secrets.token_urlsafe(32)


class Submission(TimeStampedModel):
    """Foydalanuvchi topshirgan test va uning natijasi."""

    # Natija sahifasi havola orqali ochiladi va hech qanday autentifikatsiya
    # talab qilmaydi (odam natijani do'stiga yuborishi mumkin). Manzilda
    # MongoDB `_id` sini ishlatib bo'lmaydi: ObjectId — vaqt tamg'asi,
    # mashina identifikatori va ketma-ket hisoblagichdan iborat, ya'ni bitta
    # natija havolasini bilgan odam qo'shnisinikini ham taxmin qila oladi.
    # Bu maydon esa 256 bitlik kriptografik tasodifiy qiymat.
    public_token = models.CharField(
        "havola kaliti",
        max_length=64,
        unique=True,
        db_index=True,
        default=new_public_token,
        editable=False,
    )

    quiz = models.ForeignKey(
        Quiz, verbose_name=_("test"), on_delete=models.CASCADE, related_name="submissions"
    )
    outcome = models.ForeignKey(
        Outcome,
        verbose_name=_("natija"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="submissions",
    )

    full_name = models.CharField(_("ism familiya"), max_length=120, blank=True)
    phone = models.CharField(
        _("telefon"), max_length=13, blank=True, validators=[validate_uz_phone]
    )

    # Javoblar shu ko'rinishda saqlanadi: {"<question_id>": "<option_id>"}
    answers = models.JSONField(_("javoblar"), default=dict)
    scores = models.JSONField(_("natija ballari"), default=dict)
    # Ko'nikmalar foizi: {"logic": 100, "creativity": 67, ...}
    skills = models.JSONField(_("ko'nikmalar foizi"), default=dict)

    class Meta:
        verbose_name = _("Test topshirig'i")
        verbose_name_plural = _("Test topshiriqlari")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        # Sarlavhada natijaning NOMI turadi. Ilgari bu yerda `outcome_id`,
        # ya'ni xom ObjectId chiqardi va admin sahifasining sarlavhasi
        # «Ismoil Toxirov — 6a9469d3598072182be504d4» ko'rinishida edi.
        outcome = self.outcome.tr("title") if self.outcome_id and self.outcome else "—"
        return f"{self.full_name or 'Anonim'} — {outcome}"
