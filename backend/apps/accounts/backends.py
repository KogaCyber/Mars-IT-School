"""Email yoki telefon raqam orqali kirish backend'i."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .validators import UZ_PHONE_RE, normalize_phone

UserModel = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """Foydalanuvchi email yoki telefon raqami bilan kira oladi.

    Eslatma: `iexact` kabi lookup'lar MongoDB'da regexga aylanadi va
    foydalanuvchi matni escape qilinmaydi, shuning uchun bu yerda faqat
    aniq (exact) moslik ishlatiladi — email har doim kichik harflarda saqlanadi.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (username or kwargs.get(UserModel.USERNAME_FIELD) or "").strip()
        if not identifier or not password:
            return None

        user = self._find_user(identifier)
        if user is None:
            # Timing-attack'ga qarshi: foydalanuvchi topilmasa ham hash hisoblanadi.
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def _find_user(self, identifier: str):
        # Raqamga o'xshasa — telefon, aks holda email.
        if any(char.isdigit() for char in identifier) and "@" not in identifier:
            phone = normalize_phone(identifier)
            if UZ_PHONE_RE.match(phone):
                return UserModel.objects.filter(phone=phone).first()
            return None

        return UserModel.objects.filter(email=identifier.lower()).first()
