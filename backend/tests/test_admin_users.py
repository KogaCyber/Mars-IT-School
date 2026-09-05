"""Admin paneldagi «Foydalanuvchilar» bo'limi.

Bu ro'yxat bitta savolga javob berishi kerak: «kim admin panelga kira oladi?».
Shuning uchun bu yerda uchta shart tekshiriladi:
  * ro'yxatda faqat xodimlar ko'rinadi;
  * bu yerda yaratilgan har bir foydalanuvchi darhol kira oladi;
  * formada rol, huquq guruhlari va alohida ruxsatlar umuman yo'q.
"""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group
from django.test import RequestFactory

from apps.accounts.admin import UserAdmin
from apps.accounts.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_admin():
    return UserAdmin(User, AdminSite())


@pytest.fixture
def staff(db):
    return User.objects.create_user(
        email="xodim@example.com",
        password="StrongPassw0rd!",
        first_name="Xodim",
        is_staff=True,
    )


def _request(user):
    request = RequestFactory().get("/")
    request.user = user
    return request


def test_only_staff_appear_in_list(user_admin, staff, user):
    """Panelga kira olmaydigan hisob ro'yxatda ko'rinmaydi."""
    assert not user.is_staff

    emails = set(user_admin.get_queryset(_request(staff)).values_list("email", flat=True))

    assert staff.email in emails
    assert user.email not in emails


def test_created_user_can_enter_admin(user_admin, staff):
    """`is_staff` ni qo'lda belgilash unutilib qolmasligi kerak.

    Ilgari bu katakcha formada turardi va u belgilanmaganda yangi hisob
    jimgina yaroqsiz bo'lardi: odam yaratilardi, lekin kira olmasdi.
    """
    yangi = User(email="yangi@example.com", first_name="Yangi")
    yangi.set_password("StrongPassw0rd!")

    user_admin.save_model(_request(staff), yangi, form=None, change=False)

    assert User.objects.get(email="yangi@example.com").is_staff


def test_role_groups_and_permissions_are_not_editable(user_admin):
    """Formada rol, guruh va alohida ruxsat maydonlari bo'lmasligi shart."""
    fields = {
        name
        for _, section in user_admin.fieldsets
        for name in section["fields"]
    }

    assert "role" not in fields
    assert "groups" not in fields
    assert "user_permissions" not in fields
    # Kirish huquqi endi so'ralmaydi — u avtomatik beriladi.
    assert "is_staff" not in fields


def test_add_form_asks_only_for_identity_and_password(user_admin):
    fields = set(user_admin.add_fieldsets[0][1]["fields"])

    assert fields == {"email", "first_name", "last_name", "phone", "password1", "password2"}


def test_user_model_has_no_role_field():
    """`role` modeldan butunlay olib tashlangan."""
    assert not hasattr(User, "role")
    assert "role" not in {field.name for field in User._meta.get_fields()}


def test_groups_are_removed_from_admin_menu():
    """«Huquqlar guruhlari» admin menyusida ko'rinmasligi kerak."""
    from django.contrib import admin

    assert Group not in admin.site._registry


# --- Sahifalar haqiqatan ochilishini tekshirish ------------------------------


@pytest.fixture
def admin_client(client, db):
    """Admin panelga kirgan superuser bilan HTTP klient."""
    superuser = User.objects.create_superuser(
        email="boss@example.com", password="StrongPassw0rd!", first_name="Boss"
    )
    client.force_login(superuser)
    return client


def _admin_url(path: str) -> str:
    from django.conf import settings

    return f"/{settings.ADMIN_URL}{path}"


def test_user_list_page_opens(admin_client, staff):
    response = admin_client.get(_admin_url("accounts/user/"))

    assert response.status_code == 200
    assert staff.email.encode() in response.content


def test_add_user_page_opens(admin_client):
    assert admin_client.get(_admin_url("accounts/user/add/")).status_code == 200


def test_edit_user_page_opens_without_role_or_groups(admin_client, staff):
    response = admin_client.get(_admin_url(f"accounts/user/{staff.pk}/change/"))
    html = response.content.decode()

    assert response.status_code == 200
    assert 'name="role"' not in html
    assert 'name="groups"' not in html
    assert 'name="user_permissions"' not in html
    assert 'name="is_staff"' not in html


def test_user_created_through_admin_page_can_log_in(admin_client):
    """Formani to'ldirib yaratilgan odam darhol panelga kira oladi."""
    response = admin_client.post(
        _admin_url("accounts/user/add/"),
        {
            "email": "menejer@example.com",
            "first_name": "Menejer",
            "last_name": "",
            "phone": "",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        },
    )

    assert response.status_code in (200, 302), response.status_code
    yangi = User.objects.get(email="menejer@example.com")
    assert yangi.is_staff
    assert yangi.is_active


def test_groups_page_is_gone(admin_client):
    """`auth.Group` ro'yxatdan chiqarilgani uchun sahifasi ham yo'q."""
    assert admin_client.get(_admin_url("auth/group/")).status_code == 404
