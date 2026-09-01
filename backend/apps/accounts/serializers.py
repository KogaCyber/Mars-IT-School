"""Autentifikatsiya va profil serializerlari."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
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

from .tokens import is_revoked, revoke
from .validators import normalize_phone, validate_uz_phone

User = get_user_model()


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
            "role",
            "date_joined",
        )
        read_only_fields = ("id", "email", "role", "date_joined")


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
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_phone(self, value: str) -> str:
        if not value:
            return ""
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon band.")
        return phone

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Parollar mos kelmadi."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        # Rolni tashqaridan berib bo'lmaydi — har doim o'quvchi.
        validated_data["role"] = User.Role.STUDENT
        return User.objects.create_user(password=password, **validated_data)


class TokenObtainSerializer(TokenObtainPairSerializer):
    """Token bilan birga foydalanuvchi ma'lumotini ham qaytaradi."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
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
            raise serializers.ValidationError("Joriy parol noto'g'ri.")
        return value

    def validate_new_password(self, value: str) -> str:
        validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs) -> User:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
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

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            # Eski token boshqa ishlamaydi — o'g'irlangan bo'lsa ham foydasiz.
            revoke(refresh)
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data["refresh"] = str(refresh)

        return data
