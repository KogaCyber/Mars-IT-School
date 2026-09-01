"""Vakansiyalar va ularga arizalar."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.vacancies.models import Vacancy, VacancyApplication

pytestmark = pytest.mark.django_db


@pytest.fixture
def vacancy():
    return Vacancy.objects.create(
        title_ru="Преподаватель Python",
        description_ru="Описание вакансии",
    )


def test_open_vacancies_are_public(api, vacancy):
    response = api.get(reverse("v1:vacancy-list"))
    assert response.status_code == 200
    assert response.data[0]["title"] == "Преподаватель Python"


def test_closed_vacancy_is_hidden(api, vacancy):
    vacancy.is_open = False
    vacancy.save()
    assert api.get(reverse("v1:vacancy-list")).data == []


def test_application_accepts_pdf_resume(api, vacancy):
    resume = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 test", content_type="application/pdf")
    response = api.post(
        reverse("v1:vacancy-application-create"),
        {
            "vacancy": vacancy.slug,
            "full_name": "Али Валиев",
            "phone": "901234567",
            "resume": resume,
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert VacancyApplication.objects.get().phone == "+998901234567"


def test_application_rejects_executable_resume(api, vacancy):
    payload = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
    response = api.post(
        reverse("v1:vacancy-application-create"),
        {
            "vacancy": vacancy.slug,
            "full_name": "Али",
            "phone": "901234567",
            "resume": payload,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert not VacancyApplication.objects.exists()


def test_application_rejects_oversized_resume(api, vacancy):
    big = SimpleUploadedFile("cv.pdf", io.BytesIO(b"0" * (5 * 1024 * 1024 + 1)).read())
    response = api.post(
        reverse("v1:vacancy-application-create"),
        {"vacancy": vacancy.slug, "full_name": "Али", "phone": "901234567", "resume": big},
        format="multipart",
    )

    assert response.status_code == 400
