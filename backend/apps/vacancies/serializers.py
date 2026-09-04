from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.validators import normalize_phone, validate_uz_phone
from apps.core.drf import TranslatedSerializerMixin
from apps.core.uploads import RESUME_SIGNATURES, validate_upload

from .models import Vacancy, VacancyApplication

# Rezyume uchun ruxsat etilgan kengaytmalar va maksimal hajm (5 MB).
ALLOWED_RESUME_EXTENSIONS = set(RESUME_SIGNATURES)
MAX_RESUME_SIZE = 5 * 1024 * 1024


class VacancyListSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    # Ro'yxatdagi kartochkada qisqa tavsif ham ko'rsatiladi.
    translated_fields = ("title", "description")
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = (
            "id",
            "slug",
            "employment_type",
            "salary_from",
            "salary_to",
            "is_open",
            "branch_name",
            "icon_name",
        )

    def get_branch_name(self, obj) -> str:
        return obj.branch.tr("name", self.language) if obj.branch else ""


class VacancyDetailSerializer(VacancyListSerializer):
    translated_fields = ("title", "description", "requirements", "conditions")

    class Meta(VacancyListSerializer.Meta):
        fields = VacancyListSerializer.Meta.fields


class VacancyApplicationSerializer(serializers.ModelSerializer):
    """Vakansiyaga ariza yuborish."""

    vacancy = serializers.SlugRelatedField(
        slug_field="slug", queryset=Vacancy.objects.filter(is_published=True, is_open=True)
    )
    phone = serializers.CharField(max_length=32)
    # Honeypot — botlarni ushlash uchun.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = VacancyApplication
        fields = (
            "vacancy",
            "full_name",
            "phone",
            "email",
            "cover_letter",
            "resume",
            "resume_url",
            "website",
        )

    def validate_full_name(self, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError(_("Ism juda qisqa."))
        return value

    def validate_phone(self, value: str) -> str:
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        return phone

    def validate_resume(self, file):
        """Kengaytma, hajm VA fayl mazmunini tekshiradi.

        Kengaytmani tekshirishning o'zi yetarli emas: `cv.pdf` deb nomlangan
        HTML yoki SVG fayl ichida skript bo'lishi mumkin. Shuning uchun
        faylning dastlabki baytlari (magic number) ham tekshiriladi —
        `apps/core/uploads.py`.
        """
        if file is None:
            return file

        try:
            return validate_upload(
                file, signatures=RESUME_SIGNATURES, max_bytes=MAX_RESUME_SIZE
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc

    def validate(self, attrs: dict) -> dict:
        if attrs.pop("website", ""):
            raise serializers.ValidationError(_("So'rovni yuborib bo'lmadi."))
        return attrs
