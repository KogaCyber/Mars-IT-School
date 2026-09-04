"""Umumiy kontent modellari uchun serializerlar."""

from rest_framework import serializers

from .drf import TranslatedSerializerMixin
from .models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    PageSection,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
    SectionItem,
    SiteSettings,
    SpaceFeature,
    Statistic,
)


class SiteSettingsSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("work_hours",)

    class Meta:
        model = SiteSettings
        fields = (
            "phone",
            "extra_phone",
            "email",
            "telegram_url",
            "instagram_url",
            "youtube_url",
            "facebook_url",
            "space_app_ios_url",
            "space_app_android_url",
            "privacy_policy_url",
            "promo_video_url",
            "promo_video",
            "promo_cover",
        )


class AdvantageSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = Advantage
        fields = ("id", "number", "image")


class ParentReviewSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("text", "relation")

    class Meta:
        model = ParentReview
        fields = ("id", "full_name", "photo", "video_url")


class FAQSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("question", "answer")

    class Meta:
        model = FAQ
        fields = ("id",)


class SpaceFeatureSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = SpaceFeature
        fields = ("id", "icon", "screenshot")


class StatisticSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("label",)

    class Meta:
        model = Statistic
        fields = ("id", "value")


class FounderSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("position", "bio")

    class Meta:
        model = Founder
        fields = ("id", "full_name", "photo")


class FutureBenefitSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = FutureBenefit
        fields = ("id", "icon")


class ChildSkillSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = ChildSkill
        fields = ("id", "icon", "icon_name")


class ProjectDefenceStepSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description", "label")

    class Meta:
        model = ProjectDefenceStep
        fields = ("id", "icon_name")


class SchoolFeatureSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title",)

    class Meta:
        model = SchoolFeature
        fields = ("id",)


class SectionItemSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    """Bo'lim ichidagi kartochka/bosqich/rasm."""

    translated_fields = ("value", "label", "title", "text", "note", "list")

    class Meta:
        model = SectionItem
        fields = ("id", "order", "icon_name", "icon", "image", "url")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # «Ro'yxat» maydoni admin panelda har bir band alohida qatorda yoziladi —
        # saytga massiv bo'lib boradi.
        raw_list = data.get("list") or ""
        data["list"] = [line.strip() for line in raw_list.splitlines() if line.strip()]
        return data


class PageSectionSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    """Sahifa bo'limi: sarlavhalar, matnlar, tugmalar, rasmlar va elementlar."""

    translated_fields = (
        "eyebrow",
        "title",
        "subtitle",
        "text",
        "note",
        "button_label",
        "button2_label",
    )
    items = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = ("key", "page", "order", "button_url", "button2_url", "image", "image2", "items")

    def get_items(self, obj) -> list:
        items = [item for item in obj.items.all() if item.is_published]
        return SectionItemSerializer(items, many=True, context=self.context).data
