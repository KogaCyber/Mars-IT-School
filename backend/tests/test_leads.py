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
