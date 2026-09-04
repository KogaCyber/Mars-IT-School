"""Foydalanuvchi modeli — login sifatida email ishlatiladi."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel

from .managers import UserManager
from .validators import validate_uz_phone


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        STUDENT = "student", _("O'quvchi")
        TEACHER = "teacher", _("O'qituvchi")
        ADMIN = "admin", _("Administrator")

    email = models.EmailField(_("email"), unique=True, db_index=True)
    phone = models.CharField(
        _("telefon"),
        max_length=13,
        blank=True,
        validators=[validate_uz_phone],
    )
    first_name = models.CharField(_("ism"), max_length=60)
    last_name = models.CharField(_("familiya"), max_length=60, blank=True)
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True)
    role = models.CharField(
        _("rol"), max_length=16, choices=Role.choices, default=Role.STUDENT, db_index=True
    )

    # Chiqarilgan barcha tokenlarni bir zarbada bekor qilish uchun hisoblagich.
    # Har bir JWT ichida shu qiymat `epoch` da'vosi sifatida yuriydi. Parol
    # o'zgarganda (yoki hisob bloklanganda) raqam oshadi va eski tokenlarning
    # da'vosi endi mos kelmaydi — ular darhol yaroqsiz bo'ladi.
    # `RevokedRefreshToken` faqat bitta ma'lum tokenni bekor qila oladi;
    # o'g'irlangan token esa bizga noma'lum, shuning uchun shu qiymat kerak.
    session_epoch = models.PositiveIntegerField(_("sessiya davri"), default=0, editable=False)

    is_active = models.BooleanField(_("faol"), default=True)
    is_staff = models.BooleanField(_("xodim"), default=False)
    date_joined = models.DateTimeField(_("ro'yxatdan o'tgan sana"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")
        ordering = ["-date_joined"]
        indexes = [models.Index(fields=["phone"])]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.first_name

    def revoke_all_tokens(self) -> None:
        """Shu foydalanuvchining barcha chiqarilgan JWT'larini yaroqsiz qiladi."""
        User.objects.filter(pk=self.pk).update(session_epoch=models.F("session_epoch") + 1)
        self.refresh_from_db(fields=["session_epoch"])


class RevokedRefreshToken(models.Model):
    """Bekor qilingan refresh tokenlar ro'yxati.

    simplejwt'ning `token_blacklist` ilovasi MongoDB bilan mos kelmagani uchun
    tokenlar shu model orqali bekor qilinadi: chiqishda (logout) va token
    yangilanganda eski token bu yerga yoziladi.
    """

    jti = models.CharField(_("token identifikatori"), max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        "accounts.User",
        verbose_name=_("foydalanuvchi"),
        on_delete=models.CASCADE,
        related_name="revoked_tokens",
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(_("amal qilish muddati"), db_index=True)
    revoked_at = models.DateTimeField(_("bekor qilingan vaqt"), auto_now_add=True)

    class Meta:
        verbose_name = _("Bekor qilingan token")
        verbose_name_plural = _("Bekor qilingan tokenlar")
        ordering = ["-revoked_at"]

    def __str__(self) -> str:
        return self.jti
