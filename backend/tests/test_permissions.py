"""`apps/core/permissions.py` — ruxsat sinflari.

Bu sinflar hech qachon sinalmagan edi (coverage 0%), holbuki ular
«kim nimani o'zgartira oladi» degan savolga javob beradi. Xatolik bu
yerda jimgina yuz beradi: sayt ishlashda davom etadi, lekin ma'lumot
ochilib qoladi.
"""

import pytest
from rest_framework.test import APIRequestFactory

from apps.core.permissions import IsAdminOrReadOnly, IsOwner

pytestmark = pytest.mark.django_db

factory = APIRequestFactory()


class _View:
    """DRF view o'rniga — ruxsat sinfiga faqat shu kerak."""


def _request(method: str, user=None):
    request = getattr(factory, method)("/")
    request.user = user
    return request


# --- IsAdminOrReadOnly ------------------------------------------------------


@pytest.mark.parametrize("method", ["get", "head", "options"])
def test_read_is_open_to_anonymous(method, django_user_model):
    """O'qish hamma uchun ochiq — anonim foydalanuvchi ham."""
    from django.contrib.auth.models import AnonymousUser

    assert IsAdminOrReadOnly().has_permission(_request(method, AnonymousUser()), _View())


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_write_denied_to_anonymous(method):
    from django.contrib.auth.models import AnonymousUser

    assert not IsAdminOrReadOnly().has_permission(_request(method, AnonymousUser()), _View())


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_write_denied_to_regular_user(method, user):
    """Oddiy foydalanuvchi — xodim emas, ya'ni o'zgartira olmaydi."""
    assert not user.is_staff
    assert not IsAdminOrReadOnly().has_permission(_request(method, user), _View())


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_write_allowed_for_staff(method, user):
    user.is_staff = True
    assert IsAdminOrReadOnly().has_permission(_request(method, user), _View())


def test_write_denied_when_user_missing():
    """`request.user` bo'lmasa (autentifikatsiya o'chirilgan holat) — rad etiladi."""
    assert not IsAdminOrReadOnly().has_permission(_request("post", None), _View())


# --- IsOwner ----------------------------------------------------------------


class _Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_owner_sees_own_object(user):
    obj = _Obj(user=user)
    assert IsOwner().has_object_permission(_request("get", user), _View(), obj)


def test_stranger_denied(user, django_user_model):
    other = django_user_model.objects.create_user(
        email="other@example.com", password="StrongPassw0rd!", first_name="Vali"
    )
    obj = _Obj(user=other)
    assert not IsOwner().has_object_permission(_request("get", user), _View(), obj)


def test_object_without_owner_is_denied(user):
    """Egasi ko'rsatilmagan obyekt hech kimga ochilmaydi — `None == None` tuzog'i."""
    obj = _Obj(user=None)
    assert not IsOwner().has_object_permission(_request("get", user), _View(), obj)


def test_missing_owner_field_is_denied(user):
    assert not IsOwner().has_object_permission(_request("get", user), _View(), _Obj())


def test_view_can_override_owner_field(user):
    """View `owner_field` ni o'zgartira oladi — masalan `author`."""

    class AuthorView:
        owner_field = "author"

    obj = _Obj(author=user, user=None)
    assert IsOwner().has_object_permission(_request("get", user), AuthorView(), obj)
