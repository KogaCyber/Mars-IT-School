"""Sayt bo'ylab umumiy modellar: sozlamalar, afzalliklar, fikrlar, FAQ, SPACE bo'limi."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from slugify import slugify  # python-slugify: kirill matnini lotinga o'giradi

from .translation import TranslatedModel


class TimeStampedModel(models.Model):
    """Yaratilgan/yangilangan vaqtni saqlaydigan abstrakt model."""

    created_at = models.DateTimeField(_("yaratilgan vaqt"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("yangilangan vaqt"), auto_now=True)

    class Meta:
        abstract = True


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class PublishableModel(TimeStampedModel):
    """Saytda ko'rsatiladigan/ko'rsatilmaydigan kontent uchun abstrakt model."""

    is_published = models.BooleanField(_("chop etilgan"), default=True, db_index=True)
    order = models.PositiveIntegerField(_("tartib"), default=0, db_index=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["order", "-created_at"]


class SluggedModel(models.Model):
    """Manba maydondan avtomatik slug yasaydigan abstrakt model.

    Slug URL'da ishlatiladi (ObjectId o'rniga) — havolalar o'qilishi oson bo'ladi.
    """

    slug = models.SlugField(_("slug"), max_length=160, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            # «Программирование» -> «programmirovanie»
            base = slugify(self._slug_source()) or "element"
            slug, counter = base, 1
            model = self.__class__
            while model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base}-{counter}"
            self.slug = slug[:160]
        super().save(*args, **kwargs)

    def _slug_source(self) -> str:
        return getattr(self, "title_ru", "") or getattr(self, "name_ru", "") or ""


class SiteSettings(TranslatedModel):
    """Sayt bo'yicha yagona (singleton) sozlamalar yozuvi — sarlavha va podvalda ishlatiladi."""

    phone = models.CharField(_("telefon"), max_length=32, blank=True)
    extra_phone = models.CharField(_("qo'shimcha telefon"), max_length=32, blank=True)
    email = models.EmailField(_("email"), blank=True)
    work_hours_ru = models.CharField(
        _("ish vaqti (ru)"),
        max_length=120,
        blank=True,
        help_text=_("Masalan: Ежедневно с 09:00 до 20:00"),
    )
    work_hours_uz = models.CharField(_("ish vaqti (uz)"), max_length=120, blank=True)
    work_hours_en = models.CharField(_("ish vaqti (en)"), max_length=120, blank=True)
    telegram_url = models.URLField(_("Telegram"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    youtube_url = models.URLField(_("YouTube"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    space_app_ios_url = models.URLField(_("SPACE — App Store"), blank=True)
    space_app_android_url = models.URLField(_("SPACE — Google Play"), blank=True)
    privacy_policy_url = models.URLField(_("Maxfiylik siyosati"), blank=True)

    promo_video_url = models.URLField(_("tanishtiruv videosi"), blank=True)
    promo_cover = models.ImageField(_("video muqovasi"), upload_to="promo/", blank=True)

    class Meta:
        verbose_name = _("Sayt sozlamalari")
        verbose_name_plural = _("Sayt sozlamalari")

    def __str__(self) -> str:
        return "Sayt sozlamalari"

    def save(self, *args, **kwargs):
        # Har doim bitta yozuv bo'lishini ta'minlaymiz.
        existing = SiteSettings.objects.exclude(pk=self.pk).first()
        if existing is not None:
            self.pk = existing.pk
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SiteSettings":
        return cls.objects.first() or cls.objects.create()


class Advantage(TranslatedModel, PublishableModel):
    """«Почему выбирают MARS IT School» bo'limidagi raqamlangan bloklar (01…06)."""

    number = models.CharField(_("raqam"), max_length=4, help_text=_("Masalan: 01"))

    title_ru = models.CharField(_("sarlavha (ru)"), max_length=200)
    title_uz = models.CharField(_("sarlavha (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("sarlavha (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"))
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    image = models.ImageField(_("rasm"), upload_to="advantages/", blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Afzallik")
        verbose_name_plural = _("Afzalliklar")

    def __str__(self) -> str:
        return f"{self.number} — {self.title_ru}"


class ParentReview(TranslatedModel, PublishableModel):
    """«Что говорят родители наших учеников» — ota-onalar fikri (matn yoki video)."""

    full_name = models.CharField(_("ism familiya"), max_length=120)
    relation_ru = models.CharField(
        _("kim (ru)"), max_length=120, blank=True, help_text=_("Masalan: Ali ning onasi")
    )
    relation_uz = models.CharField(_("kim (uz)"), max_length=120, blank=True)
    relation_en = models.CharField(_("kim (en)"), max_length=120, blank=True)
    photo = models.ImageField(_("rasm"), upload_to="reviews/", blank=True)
    video_url = models.URLField(_("video havola"), blank=True)

    text_ru = models.TextField(_("fikr (ru)"))
    text_uz = models.TextField(_("fikr (uz)"), blank=True)
    text_en = models.TextField(_("fikr (en)"), blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Ota-ona fikri")
        verbose_name_plural = _("Ota-onalar fikri")

    def __str__(self) -> str:
        return self.full_name


class FAQ(TranslatedModel, PublishableModel):
    """«Частые вопросы» bo'limi."""

    question_ru = models.CharField(_("savol (ru)"), max_length=255)
    question_uz = models.CharField(_("savol (uz)"), max_length=255, blank=True)
    question_en = models.CharField(_("savol (en)"), max_length=255, blank=True)

    answer_ru = models.TextField(_("javob (ru)"))
    answer_uz = models.TextField(_("javob (uz)"), blank=True)
    answer_en = models.TextField(_("javob (en)"), blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Savol-javob")
        verbose_name_plural = _("Savol-javoblar")

    def __str__(self) -> str:
        return self.question_ru


class SpaceFeature(TranslatedModel, PublishableModel):
    """«SPACE — для учеников и родителей» bo'limidagi imkoniyatlar ro'yxati."""

    title_ru = models.CharField(_("sarlavha (ru)"), max_length=200)
    title_uz = models.CharField(_("sarlavha (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("sarlavha (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    icon = models.ImageField(_("ikonka"), upload_to="space/", blank=True)
    screenshot = models.ImageField(_("ekran rasmi"), upload_to="space/", blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("SPACE imkoniyati")
        verbose_name_plural = _("SPACE imkoniyatlari")

    def __str__(self) -> str:
        return self.title_ru


class Statistic(TranslatedModel, PublishableModel):
    """Raqamlar bloki (o'quvchilar soni, filiallar va h.k.)."""

    value = models.CharField(_("qiymat"), max_length=32)

    label_ru = models.CharField(_("izoh (ru)"), max_length=120)
    label_uz = models.CharField(_("izoh (uz)"), max_length=120, blank=True)
    label_en = models.CharField(_("izoh (en)"), max_length=120, blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Statistika")
        verbose_name_plural = _("Statistika")

    def __str__(self) -> str:
        return f"{self.value} — {self.label_ru}"


class Founder(TranslatedModel, PublishableModel):
    """«Основатели» bo'limi (О нас sahifasi)."""

    full_name = models.CharField(_("ism familiya"), max_length=120)
    photo = models.ImageField(_("rasm"), upload_to="founders/", blank=True)

    position_ru = models.CharField(_("lavozim (ru)"), max_length=160)
    position_uz = models.CharField(_("lavozim (uz)"), max_length=160, blank=True)
    position_en = models.CharField(_("lavozim (en)"), max_length=160, blank=True)

    bio_ru = models.TextField(_("bio (ru)"), blank=True)
    bio_uz = models.TextField(_("bio (uz)"), blank=True)
    bio_en = models.TextField(_("bio (en)"), blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Asoschi")
        verbose_name_plural = _("Asoschilar")

    def __str__(self) -> str:
        return self.full_name


class FutureBenefit(TranslatedModel, PublishableModel):
    """«Почему это важно для будущего» — oq fondagi kartochkalar (О нас sahifasi)."""

    title_ru = models.CharField(_("sarlavha (ru)"), max_length=200)
    title_uz = models.CharField(_("sarlavha (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("sarlavha (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    icon = models.ImageField(_("ikonka"), upload_to="about/benefits/", blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Kelajak uchun afzallik")
        verbose_name_plural = _("Kelajak uchun afzalliklar")

    def __str__(self) -> str:
        return self.title_ru


class ChildSkill(TranslatedModel, PublishableModel):
    """«Какие навыки развивает ребёнок» bo'limi.

    Nomi `ChildSkill` — `teachers.Skill` (texnologiya belgilari) bilan
    aralashib ketmasligi uchun.
    """

    title_ru = models.CharField(_("ko'nikma (ru)"), max_length=200)
    title_uz = models.CharField(_("ko'nikma (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("ko'nikma (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    class Icon(models.TextChoices):
        BRAIN = "brain", _("Miya (mantiq)")
        LAYERS = "layers", _("Qatlamlar (tizimlilik)")
        TARGET = "target", _("Nishon (tahlil)")
        CUBES = "cubes", _("Kublar (loyiha)")
        CHAT = "chat", _("Suhbat (muloqot)")
        SPARK = "spark", _("Uchqun (ijod)")

    icon_name = models.CharField(
        _("ikonka"), max_length=16, choices=Icon.choices, default=Icon.BRAIN
    )
    icon = models.ImageField(
        _("o'z ikonkasi"),
        upload_to="about/skills/",
        blank=True,
        help_text=_("Yuklansa, tayyor ikonka o'rniga shu rasm ko'rsatiladi"),
    )

    class Meta(PublishableModel.Meta):
        verbose_name = _("Ko'nikma")
        verbose_name_plural = _("Ko'nikmalar")

    def __str__(self) -> str:
        return self.title_ru


class ProjectDefenceStep(TranslatedModel, PublishableModel):
    """«День, когда ребёнок защищает свой проект» bo'limidagi raqamlar ro'yxati.

    `label` — yirik qiymat («1 раз», «34», «5 мин»),
    `title` — uning ostidagi izoh («в 3 месяца», «на защиту проекта»).
    """

    class Icon(models.TextChoices):
        CALENDAR = "calendar", _("Kalendar")
        CHECKLIST = "checklist", _("Ro'yxat")
        CLOCK = "clock", _("Soat")
        USERS = "users", _("Ishtirokchilar")

    label_ru = models.CharField(
        _("qiymat (ru)"), max_length=32, help_text=_("Masalan: «1 раз», «34»")
    )
    label_uz = models.CharField(_("qiymat (uz)"), max_length=32, blank=True)
    label_en = models.CharField(_("qiymat (en)"), max_length=32, blank=True)
    icon_name = models.CharField(
        _("ikonka"), max_length=16, choices=Icon.choices, default=Icon.CALENDAR
    )

    title_ru = models.CharField(_("izoh (ru)"), max_length=200)
    title_uz = models.CharField(_("izoh (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("izoh (en)"), max_length=200, blank=True)

    description_ru = models.TextField(_("tavsif (ru)"), blank=True)
    description_uz = models.TextField(_("tavsif (uz)"), blank=True)
    description_en = models.TextField(_("tavsif (en)"), blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Loyiha himoyasi bosqichi")
        verbose_name_plural = _("Loyiha himoyasi bosqichlari")

    def __str__(self) -> str:
        return self.title_ru


class SchoolFeature(TranslatedModel, PublishableModel):
    """«MARS IT — это не просто курсы» bo'limidagi belgilangan ro'yxat."""

    title_ru = models.CharField(_("band (ru)"), max_length=200)
    title_uz = models.CharField(_("band (uz)"), max_length=200, blank=True)
    title_en = models.CharField(_("band (en)"), max_length=200, blank=True)

    class Meta(PublishableModel.Meta):
        verbose_name = _("Maktab afzalligi")
        verbose_name_plural = _("Maktab afzalliklari")

    def __str__(self) -> str:
        return self.title_ru
