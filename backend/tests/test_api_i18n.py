"""API javob matnlari so'ralgan tilda qaytishini tekshiradi.

Nega kerak: ilgari `detail` maydoni kodda qattiq yozilgan o'zbekcha matn
edi, maydon xatolari esa DRF katalogidan to'g'ri tilda kelardi. Natijada
ruscha so'rovga ARALASH javob qaytardi:

    {"detail": "Ma'lumotlar noto'g'ri.",          <- o'zbekcha
     "errors": {"phone": ["Обязательное поле."]}} <- ruscha

Frontend `detail` ni to'g'ridan-to'g'ri foydalanuvchiga ko'rsatadi
(`LeadForm.vue`), ya'ni rus tilidagi mijoz o'zbekcha xatoni ko'rardi.
"""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

LEAD_URL_NAME = "v1:lead-create"


def _post(api, lang, payload=None):
    return api.post(
        reverse(LEAD_URL_NAME),
        payload or {},
        format="json",
        HTTP_ACCEPT_LANGUAGE=lang,
    )


@pytest.mark.parametrize(
    ("lang", "expected"),
    [("uz", "Ma'lumotlar noto'g'ri."), ("ru", "Некорректные данные.")],
)
def test_validation_detail_follows_language(api, lang, expected):
    response = _post(api, lang)
    assert response.status_code == 400
    assert response.data["detail"] == expected


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("uz", "Arizangiz qabul qilindi. Tez orada bog'lanamiz."),
        ("ru", "Ваша заявка принята. Мы скоро свяжемся с вами."),
    ],
)
def test_success_detail_follows_language(api, lang, expected):
    response = _post(api, lang, {"full_name": "Ali Valiev", "phone": "+998901234567"})
    assert response.status_code == 201
    assert response.data["detail"] == expected


def test_detail_and_field_errors_share_one_language(api):
    """`detail` va `errors` bir tilda bo'lishi shart — aralash javob bo'lmasin."""
    response = _post(api, "ru")
    assert response.data["detail"] == "Некорректные данные."
    # DRF'ning o'z katalogidan keladigan maydon xatosi — ham ruscha
    assert "Обязательное поле." in response.data["errors"]["phone"]


@pytest.mark.parametrize(("lang", "expected"), [("uz", "Topilmadi."), ("ru", "Не найдено.")])
def test_not_found_is_translated_and_hides_model_name(api, lang, expected):
    """404 javobi tarjima qilinadi va model nomini oshkor qilmaydi.

    DRF `Http404` ni `NotFound` ga aylantirganda Django'ning ichki matnini
    («No News matches the given query.») saqlab qolardi — u tarjimasiz va
    ma'lumotlar bazasi tuzilishi haqida keraksiz ishora berardi.
    """
    response = api.get(
        reverse("v1:news-detail", args=["mavjud-emas-slug"]),
        HTTP_ACCEPT_LANGUAGE=lang,
    )
    assert response.status_code == 404
    assert response.data["detail"] == expected
    assert "News" not in str(response.data["detail"])


def test_honeypot_message_is_translated(api):
    response = _post(
        api,
        "ru",
        {"full_name": "Bot", "phone": "+998901234567", "website": "http://spam.example"},
    )
    assert response.status_code == 400
    assert "Не удалось отправить запрос." in str(response.data["errors"])
