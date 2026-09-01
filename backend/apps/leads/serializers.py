from rest_framework import serializers

from apps.accounts.validators import normalize_phone, validate_uz_phone
from apps.branches.models import Branch
from apps.courses.models import Course

from .models import Lead


class LeadCreateSerializer(serializers.ModelSerializer):
    """Ariza yuborish. Faqat kerakli maydonlar qabul qilinadi."""

    course = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Course.objects.filter(is_published=True),
        required=False,
        allow_null=True,
    )
    branch = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Branch.objects.filter(is_published=True),
        required=False,
        allow_null=True,
    )
    # Foydalanuvchi raqamni ixtiyoriy formatda yozishi mumkin (+998 90 123 45 67).
    phone = serializers.CharField(max_length=32)
    # Bot'larni ushlash uchun yashirin maydon (odam uni to'ldirmaydi).
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Lead
        fields = (
            "full_name",
            "phone",
            "course",
            "branch",
            "child_age",
            "comment",
            "source",
            "website",
        )

    def validate_full_name(self, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError("Ism juda qisqa.")
        return value

    def validate_phone(self, value: str) -> str:
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        return phone

    def validate_child_age(self, value):
        if value is not None and not 3 <= value <= 25:
            raise serializers.ValidationError("Yosh 3 dan 25 gacha bo'lishi kerak.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.pop("website", ""):
            # Honeypot to'ldirilgan — spam. Foydalanuvchiga sababini aytmaymiz.
            raise serializers.ValidationError("So'rovni yuborib bo'lmadi.")
        return attrs
