from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from apps.core.translation import DEFAULT_LANGUAGE, translated_fields, translation_fieldset

from .models import Option, Outcome, Question, Quiz, Skill, Submission, skill_label


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ("order", *translated_fields("text"), "outcome", "skill", "weight")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "is_published")
    fieldsets = (
        (None, {"fields": ("title_ru", "slug", "description_ru", "order", "is_published")}),
        translation_fieldset("title", "description"),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_ru", "quiz", "order")
    list_filter = ("quiz",)
    inlines = [OptionInline]
    fieldsets = (
        (None, {"fields": ("quiz", "text_ru", "image", "order")}),
        translation_fieldset("text"),
    )


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "code", "quiz")
    list_filter = ("quiz",)
    filter_horizontal = ("courses",)
    fieldsets = (
        (None, {"fields": ("quiz", "code", "title_ru", "description_ru", "image", "courses")}),
        translation_fieldset("title", "description"),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Topshirilgan test.

    Bazada javoblar `{"<savol id>": "<variant id>"}` ko'rinishida yotadi.
    Bu maydonlarni admin panelda XOM holida ko'rsatib bo'lmaydi: xodim
    ekranda faqat ObjectId ro'yxatini ko'rardi va bola nimaga javob
    berganini bilishning imkoni yo'q edi. Shuning uchun bu yerda id'lar
    savol/variant/natija matnlariga almashtirilib, jadval sifatida chiziladi.
    """

    list_display = ("created_at", "full_name", "phone", "outcome", "top_skills")
    list_filter = ("quiz", "outcome", "created_at")
    search_fields = ("full_name", "phone")
    date_hierarchy = "created_at"
    list_select_related = ("quiz", "outcome")
    readonly_fields = (
        "quiz",
        "outcome",
        "full_name",
        "phone",
        "answers_table",
        "scores_table",
        "skills_table",
        "created_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        # Topshiriq — foydalanuvchi qoldirgan yozuv, uni tahrirlab bo'lmaydi.
        return False

    # ------------------------------------------------------------------ #
    # Ro'yxat ustuni
    # ------------------------------------------------------------------ #

    @admin.display(description=_("kuchli tomonlari"))
    def top_skills(self, obj) -> str:
        """Ro'yxatda eng yuqori 3 ta ko'nikma — natijani ochmasdan ko'rinadi."""
        top = sorted((obj.skills or {}).items(), key=lambda item: -item[1])[:3]
        if not top:
            return "—"
        return ", ".join(f"{skill_label(code, DEFAULT_LANGUAGE)} {value}%" for code, value in top)

    # ------------------------------------------------------------------ #
    # Tahrirlash sahifasidagi jadvallar
    # ------------------------------------------------------------------ #

    @admin.display(description=_("Javoblar"))
    def answers_table(self, obj):
        answers = obj.answers or {}
        if not answers:
            return "—"

        questions = {
            str(question.pk): question
            for question in Question.objects.filter(pk__in=list(answers.keys()))
        }
        options = {
            str(option.pk): option
            for option in Option.objects.filter(pk__in=list(answers.values())).select_related(
                "outcome"
            )
        }

        rows = []
        # Savollar test ichidagi tartibda ko'rsatiladi, lug'at tartibida emas.
        ordered = sorted(
            answers.items(),
            key=lambda item: (
                getattr(questions.get(item[0]), "order", 0),
                str(getattr(questions.get(item[0]), "pk", "")),
            ),
        )
        for number, (question_id, option_id) in enumerate(ordered, start=1):
            question = questions.get(question_id)
            option = options.get(str(option_id))
            rows.append(
                (
                    number,
                    question.tr("text") if question else _("savol o‘chirilgan"),
                    option.tr("text") if option else _("javob o‘chirilgan"),
                    option.outcome.tr("title") if option and option.outcome else "—",
                    skill_label(option.skill, DEFAULT_LANGUAGE) if option and option.skill else "—",
                )
            )

        body = format_html_join(
            "",
            "<tr><td>{}</td><td>{}</td><td><b>{}</b></td><td>{}</td><td>{}</td></tr>",
            rows,
        )
        return format_html(
            '<table class="mars-answers">'
            "<thead><tr><th>#</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr></thead>"
            "<tbody>{}</tbody></table>",
            _("Savol"),
            _("Tanlangan javob"),
            _("Qaysi natijaga ball qo‘shdi"),
            _("Ko‘nikma"),
            body,
        )

    @admin.display(description=_("Natijalar bo‘yicha ballar"))
    def scores_table(self, obj):
        scores = obj.scores or {}
        if not scores:
            return "—"

        outcomes = {
            str(outcome.pk): outcome
            for outcome in Outcome.objects.filter(pk__in=list(scores.keys()))
        }
        ranked = sorted(scores.items(), key=lambda item: -item[1])
        best = str(obj.outcome_id) if obj.outcome_id else (ranked[0][0] if ranked else None)

        rows = [
            (
                "→" if outcome_id == best else "",
                outcomes[outcome_id].tr("title")
                if outcome_id in outcomes
                else _("natija o‘chirilgan"),
                points,
            )
            for outcome_id, points in ranked
        ]
        body = format_html_join("", "<tr><td>{}</td><td>{}</td><td><b>{}</b></td></tr>", rows)
        return format_html(
            '<table class="mars-answers">'
            "<thead><tr><th></th><th>{}</th><th>{}</th></tr></thead><tbody>{}</tbody></table>",
            _("Natija"),
            _("Ball"),
            body,
        )

    @admin.display(description=_("Ko‘nikmalar"))
    def skills_table(self, obj):
        skills = obj.skills or {}
        if not skills:
            return "—"

        # Barcha ko'nikmalar ko'rsatiladi: nol foizning yo'qligi ham ma'lumot.
        rows = [
            (skill_label(code, DEFAULT_LANGUAGE), skills.get(code, 0), skills.get(code, 0))
            for code in Skill.values
        ]
        body = format_html_join(
            "",
            '<tr><td>{}</td><td class="mars-bar-cell">'
            '<span class="mars-bar-track"><span class="mars-bar" style="width:{}%"></span></span>'
            "</td><td>{}%</td></tr>",
            rows,
        )
        return format_html('<table class="mars-answers"><tbody>{}</tbody></table>', body)
