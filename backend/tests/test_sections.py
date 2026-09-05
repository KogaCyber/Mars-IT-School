"""Sahifa bo'limlari: reestr ↔ baza sinxronizatsiyasi va ommaviy API."""

import pytest
from django.urls import reverse

from apps.core.models import PageSection, SectionItem
from apps.core.section_sync import sync_sections
from apps.core.sections import SECTIONS

pytestmark = pytest.mark.django_db


def test_sync_creates_every_registered_section():
    result = sync_sections()

    assert result["created"] == len(SECTIONS)
    assert PageSection.objects.count() == len(SECTIONS)
    # Maketdagi matn urug' fayldan ko'chadi — panel bo'sh ochilmaydi.
    assert PageSection.objects.get(key="home.hero").title_ru


def test_sync_is_idempotent():
    sync_sections()
    again = sync_sections()

    assert again["created"] == 0
    assert PageSection.objects.count() == len(SECTIONS)


def test_sync_fills_items_from_defaults():
    sync_sections()

    stages = PageSection.objects.get(key="itkids.stages")
    assert stages.items.count() == 3
    first = stages.items.first()
    # «Ro'yxat» — mavzular, har biri alohida qatorda.
    assert first.list_ru.splitlines()


def test_content_endpoint_returns_sections_by_key(api):
    sync_sections()

    response = api.get(reverse("v1:content"), {"lang": "uz"})

    assert response.status_code == 200
    hero = response.data["home.hero"]
    assert hero["title"] == PageSection.objects.get(key="home.hero").title_uz
    assert hero["items"] == []


def test_content_endpoint_splits_item_list_into_lines(api):
    sync_sections()

    stages = response_items(api, "itkids.stages")

    assert isinstance(stages[0]["list"], list)
    assert len(stages[0]["list"]) > 1


def test_unpublished_section_is_hidden(api):
    """Yashirilgan bo'lim `is_published: false` bilan, matnsiz qaytadi.

    Javobdan butunlay olib tashlansa, sayt uni «admin panelda hech narsa
    yozilmagan» deb hisoblab, maketdagi standart matn bilan ko'rsatib qo'yardi.
    """
    sync_sections()
    section = PageSection.objects.get(key="home.faq")
    section.is_published = False
    section.save()

    response = api.get(reverse("v1:content"))

    assert response.data["home.faq"]["is_published"] is False
    assert "title" not in response.data["home.faq"]
    assert response.data["home.hero"]["is_published"] is True


def test_section_that_cannot_be_hidden_stays_published(api):
    """Yashirib bo'lmaydigan bo'lim (podval) belgisi o'chirilsa ham ko'rinadi."""
    sync_sections()
    section = PageSection.objects.get(key="common.footer")
    section.is_published = False
    section.save()

    response = api.get(reverse("v1:content"))

    assert response.data["common.footer"]["is_published"] is True


def test_unpublished_item_is_hidden(api):
    sync_sections()
    section = PageSection.objects.get(key="itkids.facts")
    hidden = section.items.first()
    hidden.is_published = False
    hidden.save()

    values = [item["value"] for item in response_items(api, "itkids.facts")]

    assert hidden.value_ru not in values


def test_home_bootstrap_includes_home_sections(api):
    sync_sections()

    response = api.get(reverse("v1:home-bootstrap"))

    assert "home.hero" in response.data["sections"]
    # Umumiy bloklar ham keladi — «sinov darsi» matni bosh sahifada ishlatiladi.
    assert "common.trial" in response.data["sections"]
    # Boshqa sahifalarniki esa kerak emas.
    assert "itkids.hero" not in response.data["sections"]


def test_section_items_keep_admin_order(api):
    sync_sections()
    section = PageSection.objects.get(key="itkids.facts")
    first, last = section.items.first(), section.items.order_by("-order").first()
    first.order, last.order = 99, 1
    first.save()
    last.save()

    items = response_items(api, "itkids.facts")

    assert items[0]["value"] == last.value_ru


def response_items(api, key):
    response = api.get(reverse("v1:content"))
    return response.data[key]["items"]


def test_item_belongs_to_its_section():
    sync_sections()
    section = PageSection.objects.get(key="space.shop")

    SectionItem.objects.create(section=section, title_ru="Sovg'a", value_ru="100")

    assert section.items.filter(title_ru="Sovg'a").exists()
