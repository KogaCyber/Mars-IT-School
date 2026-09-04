"""Admin panel shablonlari uchun qo'shimcha kontekst."""

from django.conf import settings
from django.utils.translation import get_language

from .admin_site import SECTION_INDEX

#: Bo'lim eslatmasi ko'rsatiladigan admin sahifalari.
_ADMIN_VIEWS = {"changelist", "change", "add"}

#: Til almashtirgichdagi qisqa yorliqlar.
_LANGUAGE_LABELS = {
    "ru": ("RU", "Русский"),
    "uz": ("UZ", "O‘zbekcha"),
    "en": ("EN", "English"),
}


def admin_languages(request):
    """Admin paneldagi til almashtirgichi uchun tillar ro'yxati.

    `settings.ADMIN_LANGUAGES` — interfeys tillari (sayt kontenti tarjimalari
    bundan mustaqil, ular `CONTENT_LANGUAGES` orqali boshqariladi).
    """
    current = get_language() or settings.LANGUAGE_CODE
    codes = getattr(settings, "ADMIN_LANGUAGES", None) or [settings.LANGUAGE_CODE]

    languages = []
    for code in codes:
        short, title = _LANGUAGE_LABELS.get(code, (code.upper(), code))
        languages.append(
            {
                "code": code,
                "short": short,
                "title": title,
                # Joriy til — ikkitasidan qaysi biri tanlangani belgilanadi.
                "is_current": current == code or current.split("-")[0] == code,
            }
        )

    return {"mars_admin_languages": languages}


def admin_section_help(request):
    """Admin bo'limi saytning qayerini o'zgartirishini shablonga uzatadi.

    Admin URL'lari `admin:<app_label>_<model>_<view>` deb nomlangan, shundan
    model kalitini olamiz va `apps/core/admin_site.py` dagi xaritadan bo'lim
    tavsifini topamiz. Boshqa sahifalarda hech narsa qo'shilmaydi.
    """
    match = getattr(request, "resolver_match", None)
    if match is None or match.app_name != "admin" or not match.url_name:
        return {}

    name, _, view = match.url_name.rpartition("_")
    if view not in _ADMIN_VIEWS or "_" not in name:
        return {}

    app_label, _, model_name = name.partition("_")
    section = SECTION_INDEX.get(f"{app_label}.{model_name}")
    if section is None:
        return {}

    return {
        "mars_section_where": section["where"],
        "mars_section_what": section["what"],
        "mars_page_name": section["page_name"],
        "mars_page_url": section["page_url"],
    }
