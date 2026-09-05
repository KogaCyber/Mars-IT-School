"""Autentifikatsiya oqimi testlari."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import RevokedRefreshToken

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_register_creates_student_and_returns_tokens(api):
    response = api.post(
        reverse("v1:accounts:register"),
        {
            "email": "New@Example.com",
            "first_name": "Нодира",
            "phone": "901234567",
            "password": "StrongPassw0rd!",
            "password_confirm": "StrongPassw0rd!",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["user"]["email"] == "new@example.com"
    assert response.data["user"]["phone"] == "+998901234567"
    assert "access" in response.data and "refresh" in response.data


def test_register_cannot_grant_admin_access(api):
    """Ro'yxatdan o'tgan odam o'ziga admin panel huquqini bera olmaydi.

    Ilgari bu yerda `role` maydoni tekshirilardi. Rol olib tashlangach,
    kirish huquqini yagona `is_staff` hal qiladi — hujum ham, himoya ham
    endi aynan shu maydonga qaratilgan.
    """
    api.post(
        reverse("v1:accounts:register"),
        {
            "email": "hacker@example.com",
            "first_name": "H",
            "is_staff": True,
            "is_superuser": True,
            "password": "StrongPassw0rd!",
            "password_confirm": "StrongPassw0rd!",
        },
        format="json",
    )

    hacker = User.objects.get(email="hacker@example.com")
    assert not hacker.is_staff
    assert not hacker.is_superuser


def test_login_with_email_and_phone(api, user):
    user.phone = "+998901112233"
    user.save()

    for identifier in ("student@example.com", "+998901112233"):
        response = api.post(
            reverse("v1:accounts:login"),
            {"email": identifier, "password": "StrongPassw0rd!"},
            format="json",
        )
        assert response.status_code == 200, identifier
        assert response.data["user"]["email"] == user.email


def test_me_requires_authentication(api, user):
    assert api.get(reverse("v1:accounts:me")).status_code == 401

    api.force_authenticate(user)
    assert api.get(reverse("v1:accounts:me")).data["email"] == user.email


def test_logout_revokes_refresh_token(api, user):
    login = api.post(
        reverse("v1:accounts:login"),
        {"email": user.email, "password": "StrongPassw0rd!"},
        format="json",
    )
    refresh = login.data["refresh"]

    api.force_authenticate(user)
    logout = api.post(reverse("v1:accounts:logout"), {"refresh": refresh}, format="json")
    assert logout.status_code == 205
    assert RevokedRefreshToken.objects.count() == 1

    # Bekor qilingan token bilan yangilash mumkin emas.
    api.force_authenticate(None)
    refreshed = api.post(
        reverse("v1:accounts:token-refresh"), {"refresh": refresh}, format="json"
    )
    assert refreshed.status_code == 401


def test_refresh_rotates_and_revokes_previous_token(api, user):
    login = api.post(
        reverse("v1:accounts:login"),
        {"email": user.email, "password": "StrongPassw0rd!"},
        format="json",
    )
    old_refresh = login.data["refresh"]

    response = api.post(
        reverse("v1:accounts:token-refresh"), {"refresh": old_refresh}, format="json"
    )
    assert response.status_code == 200
    assert response.data["refresh"] != old_refresh

    # Eski token endi ishlamaydi.
    replay = api.post(
        reverse("v1:accounts:token-refresh"), {"refresh": old_refresh}, format="json"
    )
    assert replay.status_code == 401
