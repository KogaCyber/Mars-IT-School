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


# ---------------------------------------------------------------------------
# SSRF: tashqi manzillarga murojaat
# ---------------------------------------------------------------------------
class TestSsrfProtection:
    """`apps/core/net.py` — oq ro'yxat, IP tekshiruvi va redirect nazorati."""

    ALLOWED = ("google.com", "yandex.ru")

    def test_internal_addresses_are_rejected(self):
        """Ichki tarmoq va metadata xizmati hech qachon ochilmasligi kerak."""
        from apps.core.net import _is_public_ip

        internal = [
            "127.0.0.1",  # loopback
            "169.254.169.254",  # AWS/GCP metadata — SSRF'ning asosiy nishoni
            "10.0.0.5",  # xususiy tarmoq
            "172.16.3.1",
            "192.168.1.1",
            "100.64.0.1",  # CGNAT
            "::1",  # IPv6 loopback
            "fd00::1",  # IPv6 xususiy
            "::ffff:127.0.0.1",  # IPv4-mapped IPv6 — eng ko'p unutiladigan holat
        ]
        for address in internal:
            assert _is_public_ip(address) is False, address

        assert _is_public_ip("8.8.8.8") is True

    def test_non_http_schemes_are_rejected(self):
        from apps.core.net import is_allowed_url

        for url in (
            "file:///etc/passwd",
            "gopher://google.com/",
            "ftp://google.com/",
            "http://google.com:6379/",  # standart bo'lmagan port (Redis)
        ):
            assert is_allowed_url(url, self.ALLOWED) is False, url

    def test_host_outside_allowlist_is_rejected(self):
        from apps.core.net import is_allowed_url

        # `google.com.evil.tld` — oq ro'yxatni aldashning klassik usuli.
        assert is_allowed_url("https://google.com.evil.tld/", self.ALLOWED) is False
        assert is_allowed_url("https://evil.tld/?x=google.com", self.ALLOWED) is False

    def test_redirect_to_internal_host_is_blocked(self, monkeypatch):
        """Oq ro'yxatdagi qisqartirgich ichki manzilga yo'naltirsa — uziladi.

        Aynan shu holat ilgari ochiq edi: boshlang'ich manzil tekshirilardi,
        redirect'dan keyingi manzil esa yo'q.
        """
        from apps.core import net

        handler = net._StrictRedirectHandler(self.ALLOWED)

        class FakeRequest:
            full_url = "https://goo.gl/xyz"

        with pytest.raises(net.UnsafeUrlError):
            handler.redirect_request(
                FakeRequest(), None, 302, "Found", {}, "http://169.254.169.254/latest/meta-data/"
            )

    def test_allowlisted_domain_pointing_to_internal_ip_is_rejected(self, monkeypatch):
        """Domen oq ro'yxatda bo'lsa ham, ichki IP'ga ishora qilsa — rad etiladi.

        Bu «DNS orqali oq ro'yxatni aylanib o'tish» stsenariysi: hujumchi
        o'zi boshqaradigan domenni ichki manzilga yo'naltiradi.
        """
        import socket

        from apps.core import net

        def fake_getaddrinfo(host, *args, **kwargs):
            return [(socket.AF_INET, None, None, "", ("169.254.169.254", 80))]

        monkeypatch.setattr(net.socket, "getaddrinfo", fake_getaddrinfo)
        assert net.is_allowed_url("https://google.com/", self.ALLOWED) is False
        # Tarmoqqa chiqmaydigan tekshiruv esa domenni maqbul deb biladi —
        # ikkalasi ALOHIDA vazifa bajaradi.
        assert net.is_allowed_host("https://google.com/", self.ALLOWED) is True

    def test_host_check_never_touches_the_network(self, monkeypatch):
        """Havolani tahlil qilish DNS ishlamaganda ham ishlashi kerak."""
        from apps.core import net

        def explode(*args, **kwargs):
            raise AssertionError("is_allowed_host() tarmoqqa chiqmasligi kerak")

        monkeypatch.setattr(net.socket, "getaddrinfo", explode)
        assert net.is_allowed_host("https://yandex.ru/maps/?ll=69.2,41.3", self.ALLOWED) is True

    def test_safe_open_refuses_disallowed_url_without_network(self):
        from apps.core.net import safe_open

        assert (
            safe_open(
                "http://169.254.169.254/", allowed_hosts=self.ALLOWED, user_agent="test"
            )
            is None
        )

    def test_map_url_parser_ignores_foreign_hosts(self):
        from apps.branches.services import coords_from_map_url

        assert coords_from_map_url("https://evil.tld/?ll=41.3,69.2") is None
        assert coords_from_map_url("http://169.254.169.254/?ll=41.3,69.2") is None


# ---------------------------------------------------------------------------
# Kesh kaliti: cheksiz kalit yasab bo'lmaydi
# ---------------------------------------------------------------------------
def test_cache_key_ignores_unknown_query_params(rf):
    """Ahamiyatsiz parametr kesh kalitini o'zgartirmasligi kerak.

    Aks holda `?zzz=1..N` bilan keshni to'ldirib, barcha haqiqiy javoblarni
    siqib chiqarish mumkin edi (kesh orqali DoS).
    """
    from apps.core.cache import _cache_key

    base = _cache_key(rf.get("/api/v1/courses/"))
    assert _cache_key(rf.get("/api/v1/courses/?zzz=1")) == base
    assert _cache_key(rf.get("/api/v1/courses/?zzz=2")) == base
    # Haqiqatan ahamiyatli parametr esa kalitni o'zgartiradi.
    assert _cache_key(rf.get("/api/v1/courses/?search=python")) != base


def test_cache_key_is_stable_for_reordered_params(rf):
    from apps.core.cache import _cache_key

    assert _cache_key(rf.get("/api/v1/courses/?search=a&ordering=price")) == _cache_key(
        rf.get("/api/v1/courses/?ordering=price&search=a")
    )


# ---------------------------------------------------------------------------
# Test natijasi — taxmin qilib bo'lmaydigan havola (IDOR)
# ---------------------------------------------------------------------------
def test_quiz_result_is_not_reachable_by_object_id(api):
    """Eski manzil (`_id` bo'yicha) endi ishlamasligi kerak."""
    from apps.quiz.models import Outcome, Quiz, Submission

    quiz = Quiz.objects.create(title_ru="Тест")
    outcome = Outcome.objects.create(quiz=quiz, title_ru="Результат", code="code")
    submission = Submission.objects.create(quiz=quiz, outcome=outcome)

    assert api.get(reverse("v1:quiz-result", args=[str(submission.pk)])).status_code == 404
    assert api.get(reverse("v1:quiz-result", args=[submission.public_token])).status_code == 200


def test_quiz_result_token_is_random_and_unique():
    from apps.quiz.models import new_public_token

    tokens = {new_public_token() for _ in range(200)}
    assert len(tokens) == 200
    # 32 bayt → URL-safe base64 da 43 belgi. Taxmin qilish imkonsiz.
    assert all(len(token) >= 43 for token in tokens)


def test_quiz_result_response_does_not_leak_object_id(api):
    from apps.quiz.models import Quiz, Submission

    quiz = Quiz.objects.create(title_ru="Тест")
    submission = Submission.objects.create(quiz=quiz)

    response = api.get(reverse("v1:quiz-result", args=[submission.public_token]))
    assert response.status_code == 200
    assert "id" not in response.data
    # Shaxsiy ma'lumot ham chiqmaydi.
    assert "phone" not in response.data
    assert "full_name" not in response.data
    assert response["Cache-Control"] == "no-store, private"


# ---------------------------------------------------------------------------
# Fayl yuklash: kengaytma yetarli emas, mazmun ham tekshiriladi
# ---------------------------------------------------------------------------
class TestUploadValidation:
    @staticmethod
    def _upload(name, content):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(name, content)

    def test_html_disguised_as_pdf_is_rejected(self):
        """`cv.pdf` deb nomlangan HTML — eng keng tarqalgan yuklash hujumi."""
        from django.core.exceptions import ValidationError

        from apps.core.uploads import RESUME_SIGNATURES, validate_upload

        payload = self._upload("cv.pdf", b"<html><script>alert(1)</script></html>")
        with pytest.raises(ValidationError) as exc:
            validate_upload(payload, signatures=RESUME_SIGNATURES, max_bytes=5 * 1024 * 1024)
        assert exc.value.code == "content_mismatch"

    def test_svg_disguised_as_png_is_rejected(self):
        from django.core.exceptions import ValidationError

        from apps.core.uploads import IMAGE_SIGNATURES, validate_upload

        payload = self._upload("avatar.png", b"<svg onload=alert(1)></svg>")
        with pytest.raises(ValidationError):
            validate_upload(payload, signatures=IMAGE_SIGNATURES, max_bytes=1024)

    def test_real_pdf_passes(self):
        from apps.core.uploads import RESUME_SIGNATURES, validate_upload

        payload = self._upload("cv.pdf", b"%PDF-1.4 haqiqiy hujjat")
        assert validate_upload(
            payload, signatures=RESUME_SIGNATURES, max_bytes=5 * 1024 * 1024
        ) is payload

    def test_oversized_file_is_rejected(self):
        from django.core.exceptions import ValidationError

        from apps.core.uploads import RESUME_SIGNATURES, validate_upload

        payload = self._upload("cv.pdf", b"%PDF-1.4" + b"x" * 5000)
        with pytest.raises(ValidationError) as exc:
            validate_upload(payload, signatures=RESUME_SIGNATURES, max_bytes=1024)
        assert exc.value.code == "too_large"

    def test_unknown_extension_is_rejected(self):
        from django.core.exceptions import ValidationError

        from apps.core.uploads import RESUME_SIGNATURES, validate_upload

        payload = self._upload("shell.php", b"%PDF-1.4")
        with pytest.raises(ValidationError) as exc:
            validate_upload(payload, signatures=RESUME_SIGNATURES, max_bytes=1024)
        assert exc.value.code == "invalid_extension"

    def test_resume_endpoint_rejects_disguised_file(self, api):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from apps.vacancies.models import Vacancy, VacancyApplication

        vacancy = Vacancy.objects.create(title_ru="Преподаватель", description_ru="Описание")
        response = api.post(
            reverse("v1:vacancy-application-create"),
            {
                "vacancy": vacancy.slug,
                "full_name": "Али Валиев",
                "phone": "+998901234567",
                "resume": SimpleUploadedFile("cv.pdf", b"<html>zararli</html>"),
            },
            format="multipart",
        )
        assert response.status_code == 400
        assert not VacancyApplication.objects.exists()


def test_resume_filename_does_not_contain_candidate_name(application):
    """Fayl nomi shaxsiy ma'lumot bo'lmasligi kerak (diskda ham, sarlavhada ham)."""
    assert "cv" not in application.resume.name.rsplit("/", 1)[-1]
    assert "Али" not in application.resume.name


def test_resume_download_filename_is_neutral(client, application):
    staff = User.objects.create_user(
        email="staff-dl@example.com", password="StrongPassw0rd!", first_name="Admin", is_staff=True
    )
    client.force_login(staff)

    response = client.get(reverse("resume-download", args=[application.pk]))
    disposition = response["Content-Disposition"]
    assert "Али" not in disposition
    assert str(application.pk) in disposition
    assert response["X-Content-Type-Options"] == "nosniff"


def test_resume_download_rejects_post(client, application):
    """O'zgartiruvchi metodlar bu manzilda umuman bo'lmasligi kerak."""
    staff = User.objects.create_user(
        email="staff-post@example.com",
        password="StrongPassw0rd!",
        first_name="Admin",
        is_staff=True,
    )
    client.force_login(staff)
    assert client.post(reverse("resume-download", args=[application.pk])).status_code == 405


# ---------------------------------------------------------------------------
# Xavfsizlik sarlavhalari
# ---------------------------------------------------------------------------
def test_security_headers_are_present_on_api_responses(api):
    response = api.get(reverse("v1:site-settings"))
    assert "camera=()" in response["Permissions-Policy"]
    assert response["Cross-Origin-Resource-Policy"] == "cross-origin"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert not response.has_header("Server")


# ---------------------------------------------------------------------------
# Admin panelga IP bo'yicha cheklov
# ---------------------------------------------------------------------------
def test_admin_is_blocked_from_foreign_ip(client, settings):
    """`ADMIN_ALLOWED_IPS` to'ldirilgan bo'lsa, begona IP 404 oladi."""
    from django.conf import settings as django_settings

    settings.ADMIN_ALLOWED_IPS = ["10.10.10.0/24"]
    # Middleware ro'yxatni ishga tushishda o'qiydi — qayta yaratamiz.
    from apps.core.middleware import AdminAccessMiddleware

    middleware = AdminAccessMiddleware(lambda request: "OK")

    from django.test import RequestFactory

    factory = RequestFactory()
    outside = factory.get(f"/{django_settings.ADMIN_URL}", REMOTE_ADDR="203.0.113.9")
    assert middleware(outside).status_code == 404

    inside = factory.get(f"/{django_settings.ADMIN_URL}", REMOTE_ADDR="10.10.10.7")
    assert middleware(inside) == "OK"


def test_admin_is_open_when_allowlist_is_empty(settings):
    settings.ADMIN_ALLOWED_IPS = []
    from django.test import RequestFactory

    from apps.core.middleware import AdminAccessMiddleware

    middleware = AdminAccessMiddleware(lambda request: "OK")
    request = RequestFactory().get(f"/{settings.ADMIN_URL}", REMOTE_ADDR="203.0.113.9")
    assert middleware(request) == "OK"


# ---------------------------------------------------------------------------
# Ariza xabarnomasi so'rovni bloklamaydi
# ---------------------------------------------------------------------------
def test_lead_notification_does_not_block_the_request(api, monkeypatch):
    """Sekin SMTP butun saytni to'xtatib qo'ymasligi kerak."""
    import time

    from apps.leads import services

    started = []

    def slow_send(subject, message, lead_id):
        started.append(lead_id)
        time.sleep(0.5)

    monkeypatch.setattr(services, "_send", slow_send)

    began = time.monotonic()
    response = api.post(
        reverse("v1:lead-create"),
        {"full_name": "Али Валиев", "phone": "+998901234567", "source": "home"},
        format="json",
    )
    elapsed = time.monotonic() - began

    assert response.status_code == 201
    # Javob xabar yuborilishini KUTMAYDI.
    assert elapsed < 0.4


def test_email_subject_cannot_be_injected():
    """`full_name` orqali email sarlavhasiga qator qo'shib bo'lmaydi."""
    from apps.leads.services import _safe_subject

    subject = _safe_subject("Ali\r\nBcc: victim@example.com")
    assert "\r" not in subject
    assert "\n" not in subject


# ---------------------------------------------------------------------------
# Avatar yuklash
# ---------------------------------------------------------------------------
def test_avatar_must_be_a_real_image(api, user):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    access["epoch"] = user.session_epoch
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api.patch(
        reverse("v1:accounts:me"),
        {"avatar": SimpleUploadedFile("avatar.png", b"<svg onload=alert(1)></svg>")},
        format="multipart",
    )
    assert response.status_code == 400
