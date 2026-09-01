import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="student@example.com",
        password="StrongPassw0rd!",
        first_name="Ali",
    )


@pytest.fixture
def course(db):
    """Namunaviy kurs — ko'p testlarda kerak bo'ladi."""
    from apps.courses.models import Course, Direction

    direction = Direction.objects.create(title_ru="Программирование")
    return Course.objects.create(
        direction=direction,
        title_ru="Программирование",
        title_uz="Dasturlash",
        subtitle_ru="Курс для подростков",
        description_ru="Полное описание курса",
        price=800000,
    )
