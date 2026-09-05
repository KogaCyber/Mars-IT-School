"""Admin paneldagi «Test topshiriqlari» sahifasi.

Bu sahifani maktab xodimi o'qiydi, dasturchi emas. Bazada javoblar
`{"<savol id>": "<variant id>"}` ko'rinishida yotadi va ilgari ekranda
aynan shu xom ObjectId ro'yxati chiqardi — bola nimaga javob berganini
bilishning imkoni yo'q edi. Shuning uchun bu yerda bitta shart
tekshiriladi: sahifada matn ko'rinadi, identifikator emas.
"""

import re

import pytest
from django.contrib.admin.sites import AdminSite

from apps.quiz.admin import SubmissionAdmin
from apps.quiz.models import Option, Outcome, Question, Quiz, Skill, Submission

pytestmark = pytest.mark.django_db

OBJECT_ID = re.compile(r"\b[0-9a-f]{24}\b")


@pytest.fixture
def submission():
    quiz = Quiz.objects.create(title_ru="Профориентация", slug="proforientatsiya")
    design = Outcome.objects.create(quiz=quiz, code="design", title_ru="Дизайн")
    code = Outcome.objects.create(quiz=quiz, code="code", title_ru="Программирование")

    first = Question.objects.create(quiz=quiz, text_ru="Что интереснее?", order=1)
    second = Question.objects.create(quiz=quiz, text_ru="Чем занимаешься?", order=2)
    drawing = Option.objects.create(
        question=first, outcome=design, text_ru="Рисовать", skill=Skill.CREATIVITY
    )
    games = Option.objects.create(
        question=second, outcome=code, text_ru="Играть в игры", skill=Skill.LOGIC
    )

    return Submission.objects.create(
        quiz=quiz,
        outcome=code,
        full_name="Ismoil Toxirov",
        answers={str(first.pk): str(drawing.pk), str(second.pk): str(games.pk)},
        scores={str(design.pk): 1, str(code.pk): 2},
        skills={Skill.CREATIVITY: 50, Skill.LOGIC: 100},
    )


@pytest.fixture
def submission_admin():
    return SubmissionAdmin(Submission, AdminSite())


def test_answers_show_question_and_answer_text(submission_admin, submission):
    html = submission_admin.answers_table(submission)

    assert "Что интереснее?" in html
    assert "Рисовать" in html
    assert "Чем занимаешься?" in html
    assert "Играть в игры" in html
    # Savollar test ichidagi tartibda: 1-savol javobi 2-savolnikidan oldin.
    assert html.index("Рисовать") < html.index("Играть в игры")
    assert not OBJECT_ID.search(html)


def test_answers_name_the_outcome_and_skill(submission_admin, submission):
    html = submission_admin.answers_table(submission)

    assert "Дизайн" in html
    assert "Программирование" in html
    assert "Креативность" in html


def test_scores_are_sorted_and_mark_the_winner(submission_admin, submission):
    html = submission_admin.scores_table(submission)

    assert html.index("Программирование") < html.index("Дизайн")
    assert "→" in html
    assert not OBJECT_ID.search(html)


def test_skills_list_every_skill_with_a_percentage(submission_admin, submission):
    html = submission_admin.skills_table(submission)

    assert "100%" in html
    # Nol foizli ko'nikma ham ko'rinadi — uning yo'qligi ham ma'lumot.
    assert "Терпение" in html
    assert "0%" in html


def test_empty_submission_does_not_break_the_page(submission_admin):
    empty = Submission(answers={}, scores={}, skills={})

    assert submission_admin.answers_table(empty) == "—"
    assert submission_admin.scores_table(empty) == "—"
    assert submission_admin.skills_table(empty) == "—"


def test_deleted_question_does_not_break_the_page(submission_admin, submission):
    Question.objects.all().delete()

    html = submission_admin.answers_table(submission)

    # Savol yo'qolgan bo'lsa ham o'rnida izoh turadi, xom ObjectId emas.
    assert "Что интереснее?" not in html
    assert not OBJECT_ID.search(html)


def test_title_shows_the_outcome_name_not_its_id(submission):
    assert str(submission) == "Ismoil Toxirov — Программирование"


def test_submissions_cannot_be_edited(submission_admin, rf):
    assert submission_admin.has_add_permission(rf.get("/")) is False
    assert submission_admin.has_change_permission(rf.get("/")) is False
