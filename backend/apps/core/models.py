"""Sayt bo'ylab umumiy modellar: sozlamalar, afzalliklar, fikrlar, FAQ, SPACE bo'limi."""

from django.core.validators import FileExtensionValidator
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

    promo_video_url = models.URLField(
        _("tanishtiruv videosi — havola"),
        blank=True,
        help_text=_("YouTube yoki Vimeo havolasi. Fayl yuklansa, fayl ustun turadi."),
    )
    promo_video = models.FileField(
        _("tanishtiruv videosi — fayl"),
        upload_to="promo/",
        blank=True,
        validators=[FileExtensionValidator(["mp4", "webm", "ogv", "mov", "m4v"])],
        help_text=_("Videoni to‘g‘ridan-to‘g‘ri yuklash (mp4, webm, mov)."),
    )
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
        """Yagona sozlamalar yozuvini qaytaradi (bo'lmasa yaratadi).

        `first() or create()` ikki worker bir vaqtda chaqirsa ikkita yozuv
        yasashi mumkin edi (MongoDB'da tranzaksiya yo'q). `get_or_create`
        ham to'liq kafolat bermaydi, shuning uchun `save()` dagi singleton
        qo'rig'i ikkinchi yozuvni birinchisining ustiga qaytaradi.
        """
        instance = cls.objects.first()
        if instance is not None:
            return instance
        instance, _created = cls.objects.get_or_create()
        return instance


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


class SiteRevision(models.Model):
    """Kontent versiyasi — admin panelda biror narsa o'zgarsa o'sib boradi.

    Sayt shu raqamni kuzatadi (`/api/v1/revision/`): raqam o'zgarishi bilan
    ochiq turgan sahifa kontentni qayta yuklaydi. Shu tufayli admin paneldagi
    tahrir foydalanuvchi sahifani yangilamasa ham ko'rinadi.

    Qiymat — millisekundlardagi vaqt tamg'asi: u har doim o'sadi va bir nechta
    gunicorn worker'i bir vaqtda yozsa ham qarama-qarshilik chiqmaydi. Yagona
    hujjat barcha worker'lar uchun umumiy manba bo'lib xizmat qiladi.
    """

    value = models.BigIntegerField(_("versiya"), default=0, editable=False)
    updated_at = models.DateTimeField(_("yangilangan vaqt"), auto_now=True)

    class Meta:
        verbose_name = _("Kontent versiyasi")
        verbose_name_plural = _("Kontent versiyasi")

    def __str__(self) -> str:
        return str(self.value)


class PageSection(TranslatedModel):
    """Sayt sahifasidagi bitta bo'lim: sarlavhalar, matnlar, tugmalar va rasmlar.

    Bo'limlar ro'yxati `sections.py` reestrida belgilangan — bu yerda faqat
    ularning kontenti saqlanadi. Har bir bo'lim admin panelda o'z sahifasining
    ichida, saytdagi tartibda ko'rinadi.

    Bo'sh qoldirilgan maydon — «maketdagi standart matn qolsin» degani: sayt
    bo'sh qiymatni o'z tarjimasi bilan almashtiradi, shuning uchun bo'lim
    hech qachon bo'sh ko'rinmaydi.
    """

    key = models.CharField(_("bo'lim kaliti"), max_length=64, unique=True, editable=False)
    page = models.CharField(_("sahifa"), max_length=32, db_index=True, editable=False)
    order = models.PositiveIntegerField(_("tartib"), default=0, db_index=True, editable=False)

    eyebrow_ru = models.CharField(_("yorliq (ru)"), max_length=200, blank=True)
    eyebrow_uz = models.CharField(_("yorliq (uz)"), max_length=200, blank=True)
    eyebrow_en = models.CharField(_("yorliq (en)"), max_length=200, blank=True)

    # Sarlavhalar maketda bir necha qatorga bo'linadi, shuning uchun TextField:
    # qator uzilishi (Enter) saqlanadi va saytda shu joyda ko'chadi.
    title_ru = models.TextField(_("sarlavha (ru)"), blank=True)
    title_uz = models.TextField(_("sarlavha (uz)"), blank=True)
    title_en = models.TextField(_("sarlavha (en)"), blank=True)

    subtitle_ru = models.TextField(_("qo'shimcha sarlavha (ru)"), blank=True)
    subtitle_uz = models.TextField(_("qo'shimcha sarlavha (uz)"), blank=True)
    subtitle_en = models.TextField(_("qo'shimcha sarlavha (en)"), blank=True)

    text_ru = models.TextField(_("matn (ru)"), blank=True)
    text_uz = models.TextField(_("matn (uz)"), blank=True)
    text_en = models.TextField(_("matn (en)"), blank=True)

    note_ru = models.TextField(_("eslatma (ru)"), blank=True)
    note_uz = models.TextField(_("eslatma (uz)"), blank=True)
    note_en = models.TextField(_("eslatma (en)"), blank=True)

    button_label_ru = models.CharField(_("tugma matni (ru)"), max_length=120, blank=True)
    button_label_uz = models.CharField(_("tugma matni (uz)"), max_length=120, blank=True)
    button_label_en = models.CharField(_("tugma matni (en)"), max_length=120, blank=True)
    button_url = models.CharField(_("tugma havolasi"), max_length=300, blank=True)

    button2_label_ru = models.CharField(_("ikkinchi tugma (ru)"), max_length=120, blank=True)
    button2_label_uz = models.CharField(_("ikkinchi tugma (uz)"), max_length=120, blank=True)
    button2_label_en = models.CharField(_("ikkinchi tugma (en)"), max_length=120, blank=True)
    button2_url = models.CharField(_("ikkinchi tugma havolasi"), max_length=300, blank=True)

    image = models.ImageField(_("rasm"), upload_to="sections/", blank=True)
    image2 = models.ImageField(_("qo'shimcha rasm"), upload_to="sections/", blank=True)

    is_published = models.BooleanField(_("saytda ko'rsatilsin"), default=True)
    updated_at = models.DateTimeField(_("yangilangan vaqt"), auto_now=True)

    class Meta:
        verbose_name = _("Sahifa bo'limi")
        verbose_name_plural = _("Sahifa bo'limlari")
        ordering = ["order", "key"]

    def __str__(self) -> str:
        from .sections import SECTION_INDEX

        section = SECTION_INDEX.get(self.key)
        return str(section["name"]) if section else self.key

    @property
    def spec(self) -> dict:
        """Reestrdagi tavsif (nomi, izohi, maydonlari)."""
        from .sections import SECTION_INDEX

        return SECTION_INDEX.get(self.key, {})


class SectionItem(TranslatedModel):
    """Bo'lim ichidagi takrorlanuvchi element: kartochka, bosqich, rasm, sovg'a.

    Qaysi maydonlar ko'rinishi bo'limning reestrdagi tavsifiga bog'liq —
    masalan galereyada faqat rasm va uning tavsifi so'raladi.
    """

    section = models.ForeignKey(
        PageSection,
        verbose_name=_("bo'lim"),
        on_delete=models.CASCADE,
        related_name="items",
    )
    order = models.PositiveIntegerField(_("tartib"), default=0)

    value_ru = models.CharField(_("qiymat (ru)"), max_length=120, blank=True)
    value_uz = models.CharField(_("qiymat (uz)"), max_length=120, blank=True)
    value_en = models.CharField(_("qiymat (en)"), max_length=120, blank=True)

    label_ru = models.CharField(_("izoh (ru)"), max_length=200, blank=True)
    label_uz = models.CharField(_("izoh (uz)"), max_length=200, blank=True)
    label_en = models.CharField(_("izoh (en)"), max_length=200, blank=True)

    title_ru = models.TextField(_("sarlavha (ru)"), blank=True)
    title_uz = models.TextField(_("sarlavha (uz)"), blank=True)
    title_en = models.TextField(_("sarlavha (en)"), blank=True)

    text_ru = models.TextField(_("matn (ru)"), blank=True)
    text_uz = models.TextField(_("matn (uz)"), blank=True)
    text_en = models.TextField(_("matn (en)"), blank=True)

    note_ru = models.TextField(_("natija/eslatma (ru)"), blank=True)
    note_uz = models.TextField(_("natija/eslatma (uz)"), blank=True)
    note_en = models.TextField(_("natija/eslatma (en)"), blank=True)

    # Ro'yxat: har bir band alohida qatorda (Enter bilan ajratiladi).
    list_ru = models.TextField(_("ro'yxat (ru)"), blank=True)
    list_uz = models.TextField(_("ro'yxat (uz)"), blank=True)
    list_en = models.TextField(_("ro'yxat (en)"), blank=True)

    icon_name = models.CharField(_("ikonka nomi"), max_length=60, blank=True)
    icon = models.ImageField(_("ikonka rasmi"), upload_to="sections/icons/", blank=True)
    image = models.ImageField(_("rasm"), upload_to="sections/", blank=True)
    url = models.CharField(_("havola"), max_length=300, blank=True)

    is_published = models.BooleanField(_("ko'rsatilsin"), default=True)

    class Meta:
        verbose_name = _("Element")
        verbose_name_plural = _("Elementlar")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title_ru or self.value_ru or self.label_ru or str(_("Element"))


# ---------------------------------------------------------------------------
# Sahifa bo'yicha proksi-modellar.
#
# Django admin chap menyuda modellarni ko'rsatadi. Barcha bo'limlar bitta
# `PageSection` jadvalida yotadi, lekin kontent kirituvchi odam uchun ular
# sahifalarga bo'lingan bo'lishi kerak: «Bosh sahifa bo'limlari», «Kurs —
# IT Kids bo'limlari» va h.k. Proksi-model aynan shuni beradi: yangi jadval
# yaratilmaydi, faqat menyudagi alohida yozuv va o'z ro'yxati.
# ---------------------------------------------------------------------------
def _section_proxy(page_slug: str, class_name: str, menu_name):
    meta = type(
        "Meta",
        (),
        {
            "proxy": True,
            "app_label": "core",
            "verbose_name": menu_name,
            "verbose_name_plural": menu_name,
            "ordering": ["order", "key"],
        },
    )
    return type(
        class_name,
        (PageSection,),
        {"Meta": meta, "__module__": __name__, "page_slug": page_slug},
    )


HomeSection = _section_proxy("home", "HomeSection", _("Bosh sahifa bo'limlari"))
AboutSection = _section_proxy("about", "AboutSection", _("«Biz haqimizda» bo'limlari"))
CoursesSection = _section_proxy("courses", "CoursesSection", _("«Kurslar» sahifasi bo'limlari"))
ItKidsSection = _section_proxy("itkids", "ItKidsSection", _("«IT Kids» sahifasi bo'limlari"))
ItDevSection = _section_proxy("itdev", "ItDevSection", _("«IT dasturlash» sahifasi bo'limlari"))
SpacePageSection = _section_proxy("space", "SpacePageSection", _("«SPACE» sahifasi bo'limlari"))
NewsPageSection = _section_proxy("news", "NewsPageSection", _("«Yangiliklar» sahifasi bo'limlari"))
ContactsSection = _section_proxy(
    "contacts", "ContactsSection", _("«Kontaktlar» sahifasi bo'limlari")
)
VacanciesSection = _section_proxy(
    "vacancies", "VacanciesSection", _("«Vakansiyalar» sahifasi bo'limlari")
)
QuizPageSection = _section_proxy("quiz", "QuizPageSection", _("«Test» sahifasi bo'limlari"))
CommonSection = _section_proxy("common", "CommonSection", _("Umumiy bloklar (tugma, futer)"))

#: Sahifa kaliti → proksi-model (admin menyusini yig'ishda ishlatiladi).
SECTION_PROXIES = {
    "home": HomeSection,
    "about": AboutSection,
    "courses": CoursesSection,
    "itkids": ItKidsSection,
    "itdev": ItDevSection,
    "space": SpacePageSection,
    "news": NewsPageSection,
    "contacts": ContactsSection,
    "vacancies": VacanciesSection,
    "quiz": QuizPageSection,
    "common": CommonSection,
}
