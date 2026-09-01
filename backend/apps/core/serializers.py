"""Umumiy kontent modellari uchun serializerlar."""

from rest_framework import serializers

from .drf import TranslatedSerializerMixin
from .models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
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
