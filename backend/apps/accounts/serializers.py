"""Autentifikatsiya va profil serializerlari."""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer as BaseTokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.uploads import IMAGE_SIGNATURES, validate_upload

from .authentication import EPOCH_CLAIM, token_epoch_is_current
from .tokens import is_revoked, revoke
from .validators import normalize_phone, validate_uz_phone

User = get_user_model()

audit_log = logging.getLogger("security.audit")

#: Avatar uchun maksimal hajm (2 MB) — profil surati uchun bundan ko'pi kerak emas.
MAX_AVATAR_SIZE = 2 * 1024 * 1024


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "date_joined",
        )
        read_only_fields = ("id", "email", "date_joined")

    def validate_avatar(self, file):
        """Avatar — haqiqiy rasm bo'lishi va 2 MB dan oshmasligi kerak.

        `ImageField` Pillow orqali rasmni ochib ko'radi, lekin hajmni
        cheklamaydi va polyglot fayllarni (bir vaqtda ham rasm, ham HTML)
        o'tkazib yuborishi mumkin. Shuning uchun signatura ham tekshiriladi.
        """
        if file is None:
            return file
        try:
            return validate_upload(
                file, signatures=IMAGE_SIGNATURES, max_bytes=MAX_AVATAR_SIZE
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc


class RegisterSerializer(serializers.ModelSerializer):
    # Raqam turli ko'rinishda kelishi mumkin — normallashtirishdan oldin
    # model validatori ishlab ketmasligi uchun maydonni o'zimiz e'lon qilamiz.
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "phone", "first_name", "last_name", "password", "password_confirm")

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("Bu email allaqachon ro'yxatdan o'tgan."))
        return value

    def validate_phone(self, value: str) -> str:
        if not value:
            return ""
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(_("Bu telefon raqam allaqachon band."))
        return phone

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        # `Meta.fields` da `is_staff`/`is_superuser` yo'q, ya'ni ularni
        # so'rov orqali berib bo'lmaydi. `create_user()` esa ikkalasini ham
        # `False` qilib qo'yadi — ro'yxatdan o'tgan odam admin panelga
        # kira olmaydi.
        return User.objects.create_user(password=password, **validated_data)


class TokenObtainSerializer(TokenObtainPairSerializer):
    """Token bilan birga foydalanuvchi ma'lumotini ham qaytaradi."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Parol o'zgarganda barcha eski tokenlarni bekor qilish uchun
        # (apps/accounts/authentication.py).
        token[EPOCH_CLAIM] = user.session_epoch
        return token

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value: str) -> str:
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError(_("Joriy parol noto'g'ri."))
        return value

    def validate_new_password(self, value: str) -> str:
        validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs) -> User:
        """Parolni yangilaydi VA barcha eski sessiyalarni yopadi.

        Parol almashtirish ko'pincha "hisobimga birov kirdi" degani. Eski
        tokenlar yashab qolsa, buzg'unchi refresh token bilan yana bir hafta
        kirib turardi — ya'ni amal hech narsani hal qilmasdi.
        """
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        user.revoke_all_tokens()
        # Parol o'zgarishi — hisobni egallab olish (account takeover) ning
        # asosiy belgisi. Qayd bo'lmasa, «qachon va qayerdan o'zgardi»
        # degan savolga javob beradigan hech narsa qolmasdi.
        audit_log.info(
            "Parol o'zgartirildi: user=%s epoch=%s", user.email, user.session_epoch
        )
        return user


class TokenRefreshSerializer(BaseTokenRefreshSerializer):
    """Refresh tokenni yangilaydi va eskisini bekor qilinganlar ro'yxatiga qo'shadi.

    simplejwt'ning blacklist ilovasi MongoDB bilan ishlamagani uchun rotatsiya
    shu yerda qo'lda amalga oshiriladi.
    """

    def validate(self, attrs: dict) -> dict:
        refresh = RefreshToken(attrs["refresh"])

        if is_revoked(refresh):
            raise InvalidToken("Token bekor qilingan. Qaytadan kiring.")

        # Parol o'zgargan bo'lsa `session_epoch` oshgan va bu token — eski davrdan.
        user = User.objects.filter(pk=refresh.payload.get("user_id")).first()
        if user is None or not user.is_active:
            raise InvalidToken("Hisob mavjud emas yoki bloklangan.")
        if not token_epoch_is_current(refresh.payload, user):
            raise InvalidToken("Sessiya yakunlangan. Qaytadan kiring.")

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            # Eski token boshqa ishlamaydi — o'g'irlangan bo'lsa ham foydasiz.
            revoke(refresh)
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data["refresh"] = str(refresh)

        return data
