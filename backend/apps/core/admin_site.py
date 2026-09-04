"""Admin panelni sayt sahifalari bo'yicha guruhlaydigan maxsus `AdminSite`.

Standart Django admin modellarni "ilova" (app) bo'yicha ko'rsatadi — kontent
kirituvchi odam uchun bu tushunarsiz: «Umumiy», «Kurslar», «Yangiliklar»
degan bo'limlarda qaysi model saytning qayerini o'zgartirishi ko'rinmaydi.

Shuning uchun chap menyu va bosh sahifa saytning o'z sahifalari bo'yicha
tuziladi:

    Bosh sahifa  →  bo'limlar (Afzalliklar, Ota-onalar fikri, …)
                 →  har bir bo'limda nimani o'zgartirish mumkinligi yozilgan

Ro'yxatga olingan, lekin bu yerda ko'rsatilmagan modellar oxirgi «Boshqa»
guruhiga tushadi — hech narsa yo'qolib qolmaydi.
"""

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

# --------------------------------------------------------------------------
# Sahifa → bo'limlar xaritasi.
#
# Har bir bo'lim:  (model kaliti, saytda qayerda ko'rinadi, nimani o'zgartirish mumkin)
# --------------------------------------------------------------------------
PAGES = [
    {
        "slug": "home",
        "name": _("Bosh sahifa"),
        "url": "/",
        "hint": _("Saytning bosh sahifasida ko‘rinadigan bloklar."),
        "sections": [
            (
                "core.advantage",
                _("«Nega aynan MARS IT School» — raqamlangan kartochkalar "
                  "(«Biz haqimizda» sahifasida ham ko‘rinadi)"),
                _("Raqam (01…06), sarlavha, tavsif, rasm, tartib, chop etish"),
            ),
            (
                "core.parentreview",
                _("«Ota-onalar nima deydi» — video kartochkalar karuseli"),
                _("Ism, kimligi (ona/ota), surat, video havolasi, matn, tartib"),
            ),
            (
                "core.faq",
                _("«Ko‘p beriladigan savollar» — akkordeon"),
                _("Savol, javob, tartib, chop etish"),
            ),
            (
                "news.news",
                _("«Maktabda nima bo‘lyapti» — oxirgi yangiliklar lentasi"),
                _("Bu yerga «Yangiliklar» sahifasidagi yozuvlar tushadi"),
            ),
            (
                "teachers.teacher",
                _("«IT’da ishlaydigan o‘qituvchilar» — karusel"),
                _("Bu yerga «Biz haqimizda» sahifasidagi o‘qituvchilar tushadi"),
            ),
        ],
    },
    {
        "slug": "about",
        "name": _("Biz haqimizda"),
        "url": "/o-nas",
        "hint": _("«O нас» sahifasidagi bloklar."),
        "sections": [
            (
                "core.futurebenefit",
                _("«Nima uchun bu kelajak uchun muhim» bo‘limi"),
                _("Sarlavha, tavsif, ikonka, tartib"),
            ),
            (
                "core.childskill",
                _("«Bola qanday ko‘nikmalarni egallaydi» bo‘limi"),
                _("Sarlavha, tavsif, ikonka, tartib"),
            ),
            (
                "core.projectdefencestep",
                _("«Demo Day — bola loyihasini himoya qiladi» raqamlari"),
                _("Raqam/yorliq, izoh, ikonka, tartib"),
            ),
            (
                "core.statistic",
                _("Statistika chizig‘i (o‘quvchilar soni, yillar…)"),
                _("Qiymat, izoh, tartib"),
            ),
            (
                "core.schoolfeature",
                _("«MARS IT — bu oddiy kurslar emas» ro‘yxati"),
                _("Ro‘yxat bandlari, tartib. Yonidagi video — «Sayt sozlamalari»da"),
            ),
            (
                "core.founder",
                _("«Maktab ortida kim turadi» — asoschilar lentasi"),
                _("Ism, lavozim, surat, izoh, tartib"),
            ),
            (
                "teachers.teacher",
                _("«O‘qituvchilar» — kartochkalar karuseli"),
                _("Ism, lavozim, surat, tajriba, texnologiyalar, tartib"),
            ),
            (
                "teachers.skill",
                _("O‘qituvchi kartochkasidagi texnologiya yorliqlari"),
                _("Texnologiya nomi (Python, Figma…) — o‘qituvchiga biriktiriladi"),
            ),
        ],
    },
    {
        "slug": "courses",
        "name": _("Kurslar"),
        "url": "/kursy",
        "hint": _("Kurslar sahifasi va har bir kursning ichki sahifasi."),
        "sections": [
            (
                "courses.direction",
                _("«Yo‘nalishlar» — IT Kids va IT Dasturlash kartochkalari"),
                _("Nom, tavsif, rasm, tartib, chop etish"),
            ),
            (
                "courses.course",
                _("Kurs sahifasi (hero, narx, davomiylik, galereya, bosqichlar, savol-javoblar)"),
                _(
                    "Nom, yo‘nalish, yosh, narx, davomiylik, tavsif, rasm, galereya; "
                    "ichida — imkoniyatlar, o‘qish bosqichlari va sahifa pastidagi "
                    "savol-javoblar"
                ),
            ),
        ],
    },
    {
        "slug": "space",
        "name": _("SPACE platformasi"),
        "url": "/space",
        "hint": _("SPACE ilovasi haqidagi sahifa."),
        "sections": [
            (
                "core.spacefeature",
                _("«SPACE imkoniyatlari» — kartochkalar lentasi"),
                _("Sarlavha, tavsif, ikonka, tartib. Ilova havolalari — «Sayt sozlamalari»da"),
            ),
        ],
    },
    {
        "slug": "news",
        "name": _("Yangiliklar"),
        "url": "/novosti",
        "hint": _("Yangiliklar ro‘yxati va har bir yangilikning ichki sahifasi."),
        "sections": [
            (
                "news.newscategory",
                _("Ro‘yxat tepasidagi filtr tugmalari (Yangiliklar / Tadbirlar)"),
                _("Turkum nomi, tartib"),
            ),
            (
                "news.news",
                _("Yangilik: sarlavha, muqova, matn va fotoreportaj"),
                _(
                    "Sarlavha, turkum, qisqa matn, to‘liq matn, muqova, "
                    "chop etilgan sana; ichida — galereya rasmlari"
                ),
            ),
        ],
    },
    {
        "slug": "contacts",
        "name": _("Kontaktlar va filiallar"),
        "url": "/kontakty",
        "hint": _("Kontaktlar sahifasi, xarita va filial kartochkalari."),
        "sections": [
            (
                "branches.branch",
                _("Xaritadagi nishon va filial kartochkasi"),
                _(
                    "Nom, manzil, mo‘ljal, telefon, ish vaqti, koordinatalar, "
                    "muqova; ichida — filial galereyasi"
                ),
            ),
        ],
    },
    {
        "slug": "vacancies",
        "name": _("Vakansiyalar"),
        "url": "/vakansii",
        "hint": _("Vakansiyalar sahifasi va undan kelgan arizalar."),
        "sections": [
            (
                "vacancies.vacancy",
                _("Vakansiya kartochkasi va uning ichki sahifasi"),
                _("Lavozim, bo‘lim, ish turi, talablar, shartlar, chop etish"),
            ),
            (
                "vacancies.vacancyapplication",
                _("Vakansiyaga kelgan arizalar (faqat o‘qish uchun)"),
                _("Nomzod ma’lumotlari, rezyume, holati"),
            ),
        ],
    },
    {
        "slug": "quiz",
        "name": _("Proforientatsiya testi"),
        "url": "/test",
        "hint": _("«Kim bo‘lish kerak» testi: savollar, javoblar va natijalar."),
        "sections": [
            (
                "quiz.quiz",
                _("Test: nomi va tavsifi"),
                _("Nom, tavsif, chop etish"),
            ),
            (
                "quiz.question",
                _("Test savollari va javob variantlari"),
                _("Savol matni, tartib; ichida — javob variantlari va ballari"),
            ),
            (
                "quiz.outcome",
                _("Test natijasi sahifasi (kasb tavsiyasi)"),
                _("Natija nomi, tavsifi, tavsiya etilgan kurs, ko‘nikmalar"),
            ),
            (
                "quiz.submission",
                _("Foydalanuvchilar topshirgan testlar (faqat o‘qish uchun)"),
                _("Javoblar va chiqqan natija"),
            ),
        ],
    },
    {
        "slug": "leads",
        "name": _("Arizalar"),
        "url": "/zayavka",
        "hint": _("Saytdagi barcha shakllardan kelgan arizalar."),
        "sections": [
            (
                "leads.lead",
                _("Sinov darsi va boshqa shakllardan kelgan arizalar"),
                _("Ism, telefon, kurs, filial, izoh, holati (yangi/bog‘lanildi)"),
            ),
        ],
    },
    {
        "slug": "settings",
        "name": _("Sayt sozlamalari"),
        "url": "",
        "hint": _("Butun sayt bo‘ylab takrorlanadigan ma’lumotlar."),
        "sections": [
            (
                "core.sitesettings",
                _("Sarlavha, futer va «Biz haqimizda» sahifasidagi video"),
                _(
                    "Telefonlar, email, ish vaqti, ijtimoiy tarmoqlar, SPACE ilova "
                    "havolalari, tanishtiruv videosi (havola yoki fayl) va uning muqovasi"
                ),
            ),
        ],
    },
    {
        "slug": "staff",
        "name": _("Xodimlar va xavfsizlik"),
        "url": "",
        "hint": _("Admin panelga kirish huquqlari."),
        "sections": [
            (
                "accounts.user",
                _("Admin panel foydalanuvchilari"),
                _("Email, ism, huquqlar, parol"),
            ),
            ("auth.group", _("Huquqlar guruhlari"), _("Guruh nomi va ruxsatlar")),
        ],
    },
]

#: Havola sifatida ko'rsatilgan bo'limlar: model boshqa sahifada boshqariladi,
#: bu yerda esa u faqat "shu sahifada ham ko'rinadi" degani. Bo'lim sahifasidagi
#: eslatma asosiy sahifani ko'rsatishi uchun bular hisobga olinmaydi.
_REFERENCES = {
    ("home", "news.news"),
    ("home", "teachers.teacher"),
}


def _build_section_index():
    """`app_label.modelname` → bo'lim haqidagi ma'lumot.

    Bir model bir necha sahifada uchrashi mumkin (masalan o'qituvchilar) —
    bunda uning "asosiy" sahifasi olinadi.
    """
    index = {}
    for page in PAGES:
        for key, where, what in page["sections"]:
            if (page["slug"], key) in _REFERENCES:
                continue
            index.setdefault(
                key,
                {
                    "page_name": page["name"],
                    "page_url": page["url"],
                    "where": where,
                    "what": what,
                },
            )
    return index


#: `app_label.modelname` → {page_name, page_url, where, what}
SECTION_INDEX = _build_section_index()


class MarsAdminSite(AdminSite):
    """Chap menyuni sayt sahifalari bo'yicha tuzadigan admin."""

    site_header = _("Mars IT School — boshqaruv paneli")
    site_title = _("Mars IT School")
    index_title = _("Sahifalar bo‘yicha boshqaruv")

    def get_app_list(self, request, app_label=None):
        # Bitta ilovaning ichki sahifasi — standart ko'rinishda qoladi.
        if app_label:
            return super().get_app_list(request, app_label)

        app_dict = self._build_app_dict(request)

        # Barcha modellarni `app_label.modelname` kaliti bo'yicha yig'amiz.
        available = {}
        for app in app_dict.values():
            for model in app["models"]:
                key = f"{app['app_label']}.{model['object_name'].lower()}"
                available[key] = model

        groups = []
        used = set()

        for page in PAGES:
            models = []
            for key, where, what in page["sections"]:
                model = available.get(key)
                if model is None:
                    continue
                # Bir model bir necha sahifada ko'rinishi mumkin (masalan
                # o'qituvchilar) — har safar o'z izohi bilan.
                entry = dict(model)
                entry["section_where"] = where
                entry["section_what"] = what
                models.append(entry)
                used.add(key)

            if not models:
                continue

            groups.append(
                {
                    "name": page["name"],
                    "app_label": f"page-{page['slug']}",
                    "app_url": f"#page-{page['slug']}",
                    "has_module_perms": True,
                    "models": models,
                    "page_url": page["url"],
                    "page_hint": page["hint"],
                }
            )

        # Ro'yxatga tushmagan modellar — yo'qolib qolmasligi uchun oxirida.
        rest = [dict(model) for key, model in available.items() if key not in used]
        if rest:
            groups.append(
                {
                    "name": _("Boshqa"),
                    "app_label": "page-other",
                    "app_url": "#page-other",
                    "has_module_perms": True,
                    "models": rest,
                    "page_url": "",
                    "page_hint": _("Texnik bo‘limlar."),
                }
            )

        return groups
