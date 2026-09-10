"""Ariza yuborish testlari."""

import pytest
from django.urls import reverse

from apps.leads.models import Lead

pytestmark = pytest.mark.django_db


def test_lead_created_with_normalized_phone(api, course):
    response = api.post(
        reverse("v1:lead-create"),
        {
            "full_name": "  Али  Валиев ",
            "phone": "+998 (90) 123-45-67",
            "course": course.slug,
            "child_age": 10,
            "source": "home",
        },
        format="json",
    )
    assert response.status_code == 201

    lead = Lead.objects.get()
    assert lead.full_name == "Али Валиев"
    assert lead.phone == "+998901234567"
    assert lead.course_id == course.pk
    assert lead.status == Lead.Status.NEW


def test_honeypot_blocks_spam(api):
    response = api.post(
        reverse("v1:lead-create"),
        {"full_name": "Bot", "phone": "+998901234567", "website": "http://spam.example"},
        format="json",
    )
    assert response.status_code == 400
    assert not Lead.objects.exists()


def test_invalid_phone_rejected(api):
    response = api.post(
        reverse("v1:lead-create"), {"full_name": "Али", "phone": "12345"}, format="json"
    )
    assert response.status_code == 400
    assert not Lead.objects.exists()


def test_invalid_child_age_rejected(api):
    response = api.post(
        reverse("v1:lead-create"),
        {"full_name": "Али", "phone": "+998901234567", "child_age": 99},
        format="json",
    )
    assert response.status_code == 400


def test_lead_list_is_not_exposed(api):
    assert api.get(reverse("v1:lead-create")).status_code == 405


def test_lead_survives_unknown_course_slug(api, db):
    """Topilmagan kurs slug'i arizani YO'QOTMASLIGI kerak.

    Sayt kurs sahifasidan yuborganda `course` ga o'sha sahifaning slug'ini
    qo'yadi. Kurs nashrdan olingan (yoki baza hali to'ldirilmagan) bo'lsa,
    ilgari butun so'rov 400 bilan rad etilardi — mijozning telefoni yo'qolardi.
    """
    from apps.leads.models import Lead

    response = api.post(
        "/api/v1/leads/",
        {
            "full_name": "Malika Karimova",
            "phone": "+998901112233",
            "course": "mavjud-bo-lmagan-kurs",
            "source": "course",
        },
        format="json",
    )

    assert response.status_code == 201
    lead = Lead.objects.get(phone="+998901112233")
    assert lead.course_id is None
    # Operator odam qaysi sahifadan yozganini ko'rishi kerak.
    assert "mavjud-bo-lmagan-kurs" in lead.admin_note


def test_lead_still_links_existing_course(api, db, course):
    """Mavjud kurs esa avvalgidek bog'lanadi va izoh qo'shilmaydi."""
    from apps.leads.models import Lead

    response = api.post(
        "/api/v1/leads/",
        {
            "full_name": "Anvar Tosh",
            "phone": "+998901112244",
            "course": course.slug,
            "source": "course",
        },
        format="json",
    )

    assert response.status_code == 201
    lead = Lead.objects.get(phone="+998901112244")
    assert lead.course_id == course.pk
    assert lead.admin_note == ""
