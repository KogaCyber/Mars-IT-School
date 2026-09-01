import random

from rest_framework import serializers

from apps.accounts.validators import normalize_phone, validate_uz_phone
from apps.core.drf import TranslatedSerializerMixin

from .models import Option, Outcome, Question, Quiz, Skill, Submission, skill_label
from .services import sample_questions


class OptionSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("text",)

    class Meta:
        model = Option
        fields = ("id", "order")


class QuestionSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("text",)
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "image", "order", "options")

    def get_options(self, obj) -> list[dict]:
        """Variantlar tartibi ham aralashtiriladi — javob joyi eslab qolinmaydi."""
        options = list(obj.options.all())
        random.shuffle(options)
        return OptionSerializer(options, many=True, context=self.context).data


class OutcomeSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Outcome
        fields = ("id", "code", "image", "courses")

    def get_courses(self, obj) -> list[dict]:
        return [
            {
                "id": str(course.pk),
                "slug": course.slug,
                "title": course.tr("title", self.language),
                "card_image": course.card_image.url if course.card_image else None,
            }
            for course in obj.courses.published()
        ]


class QuizSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ("id", "slug", "questions")

    def get_questions(self, obj) -> list[dict]:
        """Har bir so'rovda savollar bazasidan tasodifiy to'plam qaytariladi."""
        return QuestionSerializer(sample_questions(obj), many=True, context=self.context).data


class SubmissionCreateSerializer(serializers.Serializer):
    """Test javoblarini qabul qiladi: `{"answers": {"<question_id>": "<option_id>"}}`."""

    answers = serializers.DictField(child=serializers.CharField(), allow_empty=False)
    full_name = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")

    def validate_phone(self, value: str) -> str:
        if not value:
            return ""
        phone = normalize_phone(value)
        validate_uz_phone(phone)
        return phone

    def validate_answers(self, value: dict) -> dict:
        if len(value) > 100:
            raise serializers.ValidationError("Javoblar soni juda ko'p.")
        return value


class SubmissionResultSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    outcome = OutcomeSerializer(read_only=True)
    matches = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ("id", "outcome", "matches", "skills", "scores", "created_at")

    def get_skills(self, obj) -> list[dict]:
        """Ko'nikmalar tahlili — foiz bo'yicha kamayish tartibida.

        Faqat shu topshiriqda o'lchangan ko'nikmalar qaytariladi: savollar
        tasodifiy tanlanadi, shuning uchun ba'zi ko'nikma umuman uchramasligi
        mumkin — uni 0% deb ko'rsatish natijani noto'g'ri talqin qilish bo'lardi.
        """
        codes = set(Skill.values)
        language = self.language
        percentages = obj.skills or {}
        return sorted(
            (
                {
                    "code": code,
                    "title": skill_label(code, language),
                    "percent": int(percent),
                }
                for code, percent in percentages.items()
                if code in codes
            ),
            key=lambda item: item["percent"],
            reverse=True,
        )

    def get_matches(self, obj) -> list[dict]:
        """Har bir yo'nalish bo'yicha moslik foizi — natija sahifasidagi diagramma.

        Ballar yig'indisi 100% ga keltiriladi; yaxlitlashdan qolgan farq eng ko'p
        ball to'plagan yo'nalishga qo'shiladi, shunda jami har doim 100 bo'ladi.
        """
        scores = {str(key): value for key, value in (obj.scores or {}).items()}
        outcomes = list(obj.quiz.outcomes.all())
        total = sum(scores.get(str(outcome.pk), 0) for outcome in outcomes)

        matches = [
            {
                "code": outcome.code,
                "title": outcome.tr("title", self.language),
                "score": scores.get(str(outcome.pk), 0),
                "percent": round(scores.get(str(outcome.pk), 0) * 100 / total) if total else 0,
            }
            for outcome in outcomes
        ]

        if matches and total:
            leader = max(matches, key=lambda item: item["score"])
            leader["percent"] += 100 - sum(item["percent"] for item in matches)

        return matches
