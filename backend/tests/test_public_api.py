"""Ochiq (public) API endpointlari testlari."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_course_list_is_public(api, course):
    response = api.get(reverse("v1:course-list"))
    assert response.status_code == 200
    assert response.data[0]["slug"] == course.slug


def test_course_returns_requested_language(api, course):
    russian = api.get(reverse("v1:course-detail", args=[course.slug]))
    assert russian.data["title"] == "Программирование"

    uzbek = api.get(reverse("v1:course-detail", args=[course.slug]), {"lang": "uz"})
    assert uzbek.data["title"] == "Dasturlash"

    # Tarjima bo'lmasa asosiy til (ru) qaytariladi.
    english = api.get(reverse("v1:course-detail", args=[course.slug]), {"lang": "en"})
    assert english.data["title"] == "Программирование"


def test_language_from_accept_language_header(api, course):
    response = api.get(reverse("v1:course-list"), HTTP_ACCEPT_LANGUAGE="uz-UZ,uz;q=0.9")
    assert response.data[0]["title"] == "Dasturlash"


def test_unpublished_course_is_hidden(api, course):
    course.is_published = False
    course.save()

    assert api.get(reverse("v1:course-list")).data == []
    assert api.get(reverse("v1:course-detail", args=[course.slug])).status_code == 404


def test_object_id_is_serialized_as_string(api, course):
    response = api.get(reverse("v1:course-detail", args=[course.slug]))
    assert isinstance(response.data["id"], str)


def test_health_endpoint(api):
    response = api.get(reverse("health"))
    assert response.status_code == 200
    assert response.data["status"] == "ok"
