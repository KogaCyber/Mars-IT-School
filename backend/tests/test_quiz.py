"""Proforientatsiya testi (quiz) mantiqi."""

import pytest
from django.urls import reverse

from apps.quiz.models import Option, Outcome, Question, Quiz

pytestmark = pytest.mark.django_db


@pytest.fixture
def quiz(course):
    quiz = Quiz.objects.create(title_ru="Профориентация", slug="proforientatsiya")

    design = Outcome.objects.create(quiz=quiz, code="design", title_ru="Дизайн")
    code = Outcome.objects.create(quiz=quiz, code="code", title_ru="Программирование")
    code.courses.add(course)

    first = Question.objects.create(quiz=quiz, text_ru="Что интереснее?", order=1)
    second = Question.objects.create(quiz=quiz, text_ru="Чем занимаешься?", order=2)

    Option.objects.create(question=first, outcome=design, text_ru="Рисовать", weight=1)
    Option.objects.create(question=first, outcome=code, text_ru="Собирать роботов", weight=1)
    Option.objects.create(question=second, outcome=code, text_ru="Играть в игры", weight=2)

    return quiz


def test_quiz_returns_questions_with_options(api, quiz):
    response = api.get(reverse("v1:quiz-detail", args=[quiz.slug]))
    assert response.status_code == 200
    assert len(response.data["questions"]) == 2

    # Savollar tartibi aralashtiriladi, shuning uchun matni bo'yicha topamiz.
    first = next(q for q in response.data["questions"] if q["text"] == "Что интереснее?")
    assert len(first["options"]) == 2


def test_quiz_returns_random_subset_of_questions(api, quiz):
    """Savollar bazasi katta bo'lsa — har safar tasodifiy 20 tasi qaytadi."""
    outcome = quiz.outcomes.get(code="code")
    for number in range(30):
        question = Question.objects.create(quiz=quiz, text_ru=f"Вопрос {number}", order=number)
        Option.objects.create(question=question, outcome=outcome, text_ru="Да", weight=1)

    seen: set[str] = set()
    for _ in range(5):
        response = api.get(reverse("v1:quiz-detail", args=[quiz.slug]))
        assert len(response.data["questions"]) == quiz.questions_per_attempt == 20
        seen.update(item["id"] for item in response.data["questions"])

    # Bir necha so'rovda 20 tadan ko'p turli savol ko'rinadi — to'plam almashadi.
    assert len(seen) > 20


def test_tie_is_resolved_by_first_answer(api, quiz):
    """Ballar teng bo'lsa — birinchi javobdagi yo'nalish g'olib bo'ladi."""
    first, second = quiz.questions.all()
    design_option = first.options.get(text_ru="Рисовать")
    code_option = first.options.get(text_ru="Собирать роботов")
    tie_question = Question.objects.create(quiz=quiz, text_ru="Ещё вопрос", order=3)
    tie_option = Option.objects.create(
        question=tie_question, outcome=quiz.outcomes.get(code="code"), text_ru="Код", weight=1
    )
    del second, code_option

    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {
            "answers": {
                str(first.pk): str(design_option.pk),
                str(tie_question.pk): str(tie_option.pk),
            }
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["outcome"]["code"] == "design"


def test_submit_returns_outcome_with_highest_score(api, quiz, course):
    first, second = quiz.questions.all()
    code_option = first.options.get(text_ru="Собирать роботов")
    games_option = second.options.get(text_ru="Играть в игры")

    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {
            "answers": {str(first.pk): str(code_option.pk), str(second.pk): str(games_option.pk)},
            "full_name": "Али",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["outcome"]["code"] == "code"
    assert response.data["outcome"]["courses"][0]["slug"] == course.slug


def test_submit_ignores_unknown_option_ids(api, quiz):
    first = quiz.questions.first()
    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {str(first.pk): "000000000000000000000000"}},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["outcome"] is None


def test_result_can_be_reopened_by_link(api, quiz):
    first = quiz.questions.first()
    option = first.options.first()
    created = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {str(first.pk): str(option.pk)}},
        format="json",
    )

    response = api.get(reverse("v1:quiz-result", args=[created.data["id"]]))
    assert response.status_code == 200
    assert response.data["id"] == created.data["id"]


def test_result_returns_match_percentages(api, quiz):
    """Natija sahifasidagi «Совпадение» foizlari: jami har doim 100%."""
    first, second = quiz.questions.all()
    code_option = first.options.get(text_ru="Собирать роботов")
    games_option = second.options.get(text_ru="Играть в игры")

    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {str(first.pk): str(code_option.pk), str(second.pk): str(games_option.pk)}},
        format="json",
    )

    matches = {item["code"]: item["percent"] for item in response.data["matches"]}
    assert sum(matches.values()) == 100
    assert matches["code"] > matches["design"]


def test_result_returns_only_measured_skills(api, quiz):
    """Test o'lchamagan ko'nikma natijaga 0% bo'lib tushmasligi kerak."""
    first = quiz.questions.first()
    option = first.options.first()
    option.skill = "logic"
    option.save(update_fields=["skill"])

    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {str(first.pk): str(option.pk)}},
        format="json",
    )

    codes = [item["code"] for item in response.data["skills"]]
    assert codes == ["logic"]
    assert response.data["skills"][0]["percent"] == 100
