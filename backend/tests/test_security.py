"""Xavfsizlik tuzatishlari uchun regressiya testlari.

Har bir test aniq bir kamchilikni qaytib kelmasligini qo'riqlaydi.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.vacancies.models import Vacancy, VacancyApplication

User = get_user_model()
pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Noto'g'ri ObjectId → 500 emas, 400/404
# ---------------------------------------------------------------------------
def test_invalid_result_id_returns_404_not_500(api):
    """Buzuq havola (`/test/rezultat/abc`) serverni yiqitmasligi kerak."""
    response = api.get(reverse("v1:quiz-result", args=["mana-bu-id-emas"]))
    assert response.status_code == 404


def test_quiz_submit_with_garbage_answer_keys_returns_400(api):
    from apps.quiz.models import Quiz

    quiz = Quiz.objects.create(title_ru="Тест")
    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {"abc": "def"}},
        format="json",
    )
    assert response.status_code == 400


def test_quiz_submit_keeps_valid_answers_and_drops_broken_ones(api):
    """Bitta yaroqsiz kalit butun topshiriqni buzmasligi kerak."""
    from apps.quiz.models import Option, Outcome, Question, Quiz

    quiz = Quiz.objects.create(title_ru="Тест", questions_per_attempt=0)
    outcome = Outcome.objects.create(quiz=quiz, title_ru="Программирование", code="code")
    question = Question.objects.create(quiz=quiz, text_ru="Савол")
    option = Option.objects.create(question=question, outcome=outcome, text_ru="Ҳа", weight=3)

    response = api.post(
        reverse("v1:quiz-submit", args=[quiz.slug]),
        {"answers": {str(question.pk): str(option.pk), "yaroqsiz": "kalit"}},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["outcome"]["code"] == "code"


# ---------------------------------------------------------------------------
# Rezyume — shaxsiy ma'lumot
# ---------------------------------------------------------------------------
@pytest.fixture
def application(settings):
    vacancy = Vacancy.objects.create(title_ru="Преподаватель", description_ru="Описание")
    from django.core.files.uploadedfile import SimpleUploadedFile

    item = VacancyApplication.objects.create(
        vacancy=vacancy, full_name="Али Валиев", phone="+998901234567"
    )
    item.resume.save("cv.pdf", SimpleUploadedFile("cv.pdf", b"%PDF-1.4 maxfiy"), save=True)
    return item


def test_resume_is_stored_outside_public_media(application, settings):
    """Fayl ochiq `MEDIA_ROOT` ichida BO'LMASLIGI kerak.

    WhiteNoise butun `MEDIA_ROOT` ni uzatadi — u yerdagi rezyume manzilini
    taxmin qilgan har kim yuklab olardi.
    """
    path = application.resume.path
    assert str(settings.PRIVATE_MEDIA_ROOT) in path
    assert str(settings.MEDIA_ROOT) not in path


def test_resume_has_no_public_url(application):
    """`.url` ataylab xatolik beradi — tasodifan ochiq havola chiqib ketmasin."""
    with pytest.raises(ValueError):
        _ = application.resume.url


def test_resume_download_requires_staff(client, application):
    url = reverse("resume-download", args=[application.pk])

    assert client.get(url).status_code == 403

    student = User.objects.create_user(
        email="student@example.com", password="StrongPassw0rd!", first_name="Ali"
    )
    client.force_login(student)
    assert client.get(url).status_code == 403


def test_staff_can_download_resume(client, application):
    staff = User.objects.create_user(
        email="staff@example.com", password="StrongPassw0rd!", first_name="Admin", is_staff=True
    )
    client.force_login(staff)

    response = client.get(reverse("resume-download", args=[application.pk]))
    assert response.status_code == 200
    assert response["Content-Disposition"].startswith("attachment")
    assert b"maxfiy" in b"".join(response.streaming_content)


# ---------------------------------------------------------------------------
# Parol o'zgarganda barcha tokenlar bekor bo'ladi
# ---------------------------------------------------------------------------
def test_password_change_invalidates_existing_tokens(api, user):
    refresh = RefreshToken.for_user(user)
    refresh["epoch"] = user.session_epoch
    access = refresh.access_token
    access["epoch"] = user.session_epoch

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert api.get(reverse("v1:accounts:me")).status_code == 200

    response = api.post(
        reverse("v1:accounts:password-change"),
        {"old_password": "StrongPassw0rd!", "new_password": "YangiKuchliParol9!"},
        format="json",
    )
    assert response.status_code == 200

    # Eski access token endi ishlamaydi — o'g'irlangan bo'lsa ham foydasiz.
    assert api.get(reverse("v1:accounts:me")).status_code == 401

    # Eski refresh token ham yaroqsiz.
    api.credentials()
    refreshed = api.post(
        reverse("v1:accounts:token-refresh"), {"refresh": str(refresh)}, format="json"
    )
    assert refreshed.status_code == 401


# ---------------------------------------------------------------------------
# Ro'yxatdan o'tish standart bo'yicha yopiq
# ---------------------------------------------------------------------------
def test_registration_is_closed_by_default(api, settings):
    settings.PUBLIC_REGISTRATION_ENABLED = False
    response = api.post(
        reverse("v1:accounts:register"),
        {
            "email": "yangi@example.com",
            "first_name": "Ali",
            "password": "StrongPassw0rd!",
            "password_confirm": "StrongPassw0rd!",
        },
        format="json",
    )
    assert response.status_code == 403
    assert not User.objects.filter(email="yangi@example.com").exists()


# ---------------------------------------------------------------------------
# Chiqish access tokensiz ham ishlaydi
# ---------------------------------------------------------------------------
def test_logout_works_without_valid_access_token(api, user):
    """Access token 15 daqiqada tugaydi — chiqish shunda ham ishlashi kerak."""
    refresh = RefreshToken.for_user(user)
    response = api.post(reverse("v1:accounts:logout"), {"refresh": str(refresh)}, format="json")
    assert response.status_code == 205


# ---------------------------------------------------------------------------
# Admin kiritadigan ma'lumot validatsiyasi
# ---------------------------------------------------------------------------
def test_accent_color_must_be_hex():
    """Noto'g'ri rang admin panelda ushlanadi, saytda emas."""
    from django.core.exceptions import ValidationError

    from apps.courses.models import Course

    course = Course(title_ru="Курс", description_ru="Описание", accent_color="red")
    with pytest.raises(ValidationError) as exc:
        course.full_clean()
    assert "accent_color" in exc.value.error_dict

    course.accent_color = "#E94921"
    course.full_clean()  # xatolik bo'lmasligi kerak


def test_branch_coordinates_are_range_checked():
    from django.core.exceptions import ValidationError

    from apps.branches.models import Branch

    branch = Branch(name_ru="Филиал", address_ru="Адрес", latitude=999, longitude=41.3)
    with pytest.raises(ValidationError) as exc:
        branch.full_clean()
    assert "latitude" in exc.value.error_dict


# ---------------------------------------------------------------------------
# Bosh sahifa javobi cheksiz o'smaydi
# ---------------------------------------------------------------------------
def test_home_bootstrap_limits_each_section(api):
    from apps.core.models import FAQ
    from apps.core.views import HOME_SECTION_LIMIT

    for index in range(HOME_SECTION_LIMIT + 5):
        FAQ.objects.create(question_ru=f"Вопрос {index}", answer_ru="Ответ")

    response = api.get(reverse("v1:home-bootstrap"))
    assert response.status_code == 200
    assert len(response.data["faqs"]) == HOME_SECTION_LIMIT


# ---------------------------------------------------------------------------
# Admin qidiruvi regex metabelgilaridan buzilmaydi
# ---------------------------------------------------------------------------
def test_admin_search_survives_regex_metacharacters(client):
    """Xodim telefon bo'yicha `+998` deb qidirsa 500 bo'lmasligi kerak."""
    from apps.leads.models import Lead

    Lead.objects.create(full_name="Али Валиев", phone="+998901234567")
    staff = User.objects.create_user(
        email="admin2@example.com",
        password="StrongPassw0rd!",
        first_name="Admin",
        is_staff=True,
        is_superuser=True,
    )
    client.force_login(staff)

    from django.conf import settings

    url = f"/{settings.ADMIN_URL}leads/lead/?q=%2B998"
    assert client.get(url).status_code == 200
