from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounts.validators import normalize_phone, validate_uz_phone
from apps.branches.models import Branch
from apps.courses.models import Course

from .models import Lead


class ForgivingSlugField(serializers.SlugRelatedField):
    """Topilmagan slug tufayli ARIZA YO'QOLMAYDI.

    Nega kerak: sayt kurs sahifasidan ariza yuborganda `course` maydoniga
    o'sha sahifaning slug'ini qo'yadi. Agar kurs shu orada nashrdan olingan,
    nomi o'zgargan yoki odam sahifani uzoq ochiq ushlab turgan bo'lsa,
    standart `SlugRelatedField` butun so'rovni 400 bilan rad etardi — mijoz
    formani to'ldiribdi, telefonini qoldiribdi, lekin maktab buni umuman
    ko'rmasdi. Bog'lanish yo'qolgani arizani yo'qotish uchun sabab emas.

    Topilmagan qiymat `context["unresolved"]` ga yoziladi va `create()` uni
    admin izohiga qo'shadi — operator odam qaysi sahifadan yozganini biladi.
    """

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            self.context.setdefault("unresolved", {})[self.field_name] = str(data)[:100]
            return None


class LeadCreateSerializer(serializers.ModelSerializer):
    """Ariza yuborish. Faqat kerakli maydonlar qabul qilinadi."""

    course = ForgivingSlugField(
        slug_field="slug",
        queryset=Course.objects.filter(is_published=True),
        required=False,
        allow_null=True,
    )
    branch = ForgivingSlugField(
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
            raise serializers.ValidationError(_("Ism juda qisqa."))
        return value

    def validate_phone(self, value: str) -> str:
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        return phone

    def validate_child_age(self, value):
        if value is not None and not 3 <= value <= 25:
            raise serializers.ValidationError(_("Yosh 3 dan 25 gacha bo'lishi kerak."))
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.pop("website", ""):
            # Honeypot to'ldirilgan — spam. Foydalanuvchiga sababini aytmaymiz.
            raise serializers.ValidationError(_("So'rovni yuborib bo'lmadi."))
        return attrs

    def create(self, validated_data: dict) -> Lead:
        """Bog'lanmagan slug'larni admin izohiga yozib qo'yadi.

        Ariza baribir saqlanadi; izoh esa operatorga odam qaysi sahifadan
        yozganini ko'rsatadi — aks holda bu ma'lumot izsiz yo'qolardi.
        """
        unresolved = self.context.get("unresolved") or {}
        if unresolved:
            note = "; ".join(f"{key}={value}" for key, value in sorted(unresolved.items()))
            validated_data["admin_note"] = (
                f"Saytda topilmagan bog'lanish: {note}. "
                "Kurs/filial nashrdan olingan yoki nomi o'zgargan bo'lishi mumkin."
            )
        return super().create(validated_data)
