"""Sayt sahifalari va ulardagi bo'limlar reestri.

Nega kerak: ilgari saytning ko'p matni va rasmi frontend kodida (`i18n/messages`,
`data/*.js`) qat'iy yozilgan edi — admin panelda ularni o'zgartirib bo'lmasdi.
Endi har bir sahifa bo'limi `PageSection` yozuvi sifatida saqlanadi, admin panel
esa aynan sayt tartibida ko'rsatadi:

    Bosh sahifa  →  1. Hero  →  sarlavha, matn, tugmalar, rasm
                 →  2. Afzalliklar  →  yorliq, sarlavha, matn
                 →  …

Reestr — yagona haqiqat manbai: qaysi bo'limlar bor, ular qaysi sahifada,
qanday tartibda va qaysi maydonlar tahrirlanadi. Model hamma maydonni saqlaydi,
admin esa faqat shu yerda sanab o'tilganlarini ko'rsatadi — shuning uchun
bo'lim shakli faqat kerakli maydonlardan iborat bo'ladi.
"""

from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------------------------
# Sahifalar
# ---------------------------------------------------------------------------
#: (kalit, nomi, saytdagi manzili)
PAGES: list[tuple[str, str, str]] = [
    ("home", _("Bosh sahifa"), "/"),
    ("about", _("Biz haqimizda"), "/o-nas"),
    ("courses", _("Kurslar (ro'yxat)"), "/kursy"),
    ("itkids", _("Kurs — IT Kids"), "/kursy/it-kids"),
    ("itdev", _("Kurs — IT dasturlash"), "/kursy/it-razrabotka"),
    ("space", _("SPACE platformasi"), "/space"),
    ("news", _("Yangiliklar"), "/novosti"),
    ("contacts", _("Kontaktlar"), "/kontakty"),
    ("vacancies", _("Vakansiyalar"), "/vakansii"),
    ("quiz", _("Proforientatsiya testi"), "/test"),
    ("common", _("Umumiy bloklar"), ""),
]

PAGE_CHOICES = [(slug, name) for slug, name, _url in PAGES]
PAGE_NAMES = {slug: name for slug, name, _url in PAGES}
PAGE_URLS = {slug: url for slug, _name, url in PAGES}

# ---------------------------------------------------------------------------
# Maydon nomlari (model'dagi tarjima qilinadigan asoslar)
# ---------------------------------------------------------------------------
#: Bo'limda ishlatilishi mumkin bo'lgan barcha matn maydonlari.
TEXT_FIELDS = ("eyebrow", "title", "subtitle", "text", "note", "button_label", "button2_label")
#: Tarjimasiz maydonlar.
PLAIN_FIELDS = ("button_url", "button2_url", "image", "image2")

#: Elementlar (kartochkalar) uchun maydonlar.
ITEM_TEXT_FIELDS = ("value", "label", "title", "text", "note", "list")
ITEM_PLAIN_FIELDS = ("icon_name", "icon", "image", "url")


def _s(
    key, page, name, hint, fields, *, items=None, item_name=None, item_hint="", hideable=True
):
    """Bitta bo'lim tavsifi.

    `hideable=False` — bo'limni saytdan butunlay yashirib bo'lmaydi: u alohida
    blok emas, balki sayt ishlashi uchun zarur matn (test qadamlari, umumiy
    tugmalar matni, podval). Bunday bo'limda admin panelda «saytda
    ko'rsatilsin» belgisi ko'rsatilmaydi.
    """
    return {
        "key": key,
        "page": page,
        "name": name,
        "hint": hint,
        "fields": tuple(fields),
        "items": tuple(items) if items else (),
        "item_name": item_name or _("Element"),
        "item_hint": item_hint,
        "hideable": hideable,
    }


# ---------------------------------------------------------------------------
# Bo'limlar. Tartib — saytdagi tartib (yuqoridan pastga).
# ---------------------------------------------------------------------------
SECTIONS: list[dict] = [
    # ---------------------------- Bosh sahifa ----------------------------
    _s(
        "home.hero", "home",
        _("1. Hero — «Kelajakni yaratishni o'rganamiz»"),
        _("Sahifaning eng tepasidagi katta blok: sarlavha, matn, ikkita tugma "
          "va o'ngdagi astronavt rasmi."),
        ("title", "text", "subtitle", "button_label", "button2_label", "image"),
    ),
    _s(
        "home.advantages", "home",
        _("2. «Nega MARS IT School ni tanlashadi» — sarlavha"),
        _("Blok sarlavhasi va izohi. Raqamlangan kartochkalar — «Afzalliklar» "
          "bo'limida (shu sahifa menyusida)."),
        ("eyebrow", "title", "text"),
    ),
    _s(
        "home.space", "home",
        _("3. SPACE platformasi bloki"),
        _("Bosh sahifadagi SPACE reklama bloki: yorliq, sarlavha va matn."),
        ("eyebrow", "title", "text", "button_label", "image"),
    ),
    _s(
        "home.platform", "home",
        _("3.1. SPACE maketi — chap menyu va ekran rasmlari"),
        _("SPACE blokidagi platforma maketi. Har bir element — chapdagi bitta "
          "tugma: nomi, ikonkasi va tugma bosilganda o'ngda ko'rinadigan ekran "
          "rasmi. Tugmalar sonini xohlagancha o'zgartirish mumkin."),
        (),
        items=("title", "icon_name", "icon", "image"),
        item_name=_("Menyu tugmasi"),
        item_hint=_(
            "«Sarlavha» — tugma matni. «Rasm» — shu tugma bosilganda o'ngda "
            "ko'rsatiladigan ekran rasmi (bo'sh qoldirilsa, tayyor jonli maket "
            "chiziladi). «Ikonka nomi» — book, play, star, trophy, chat, bag; "
            "o'z ikonkangizni «ikonka rasmi»ga yuklashingiz ham mumkin."
        ),
    ),
    _s(
        "home.news", "home",
        _("4. «Maktabda nimalar bo'lyapti» — sarlavha"),
        _("Yangiliklar lentasi tepasidagi matn va tugma. Yangiliklarning o'zi — "
          "«Yangiliklar» sahifasida."),
        ("eyebrow", "title", "button_label"),
    ),
    _s(
        "home.team", "home",
        _("5. «IT'da ishlaydigan o'qituvchilar» — sarlavha"),
        _("O'qituvchilar karuseli tepasidagi matn. O'qituvchilar — «Biz haqimizda» "
          "sahifasida."),
        ("eyebrow", "title"),
    ),
    _s(
        "home.reviews", "home",
        _("6. «Ota-onalar nima deydi» — sarlavha"),
        _("Fikrlar karuseli tepasidagi matn. Fikrlarning o'zi — «Ota-onalar fikri» "
          "bo'limida."),
        ("eyebrow", "title", "text"),
    ),
    _s(
        "home.faq", "home",
        _("7. «Ko'p beriladigan savollar» — sarlavha"),
        _("Akkordeon tepasidagi matn va yonidagi rasm. Savollar — «Savol-javoblar» "
          "bo'limida."),
        ("eyebrow", "title", "image"),
    ),

    # --------------------------- Biz haqimizda ---------------------------
    _s(
        "about.hero", "about",
        _("1. Hero — «O'rganamiz. Yaratamiz. Rivojlanamiz.»"),
        _("Sahifa tepasidagi sarlavha va fon rasmi."),
        ("title", "image"),
    ),
    _s(
        "about.future", "about",
        _("2. «Nega bu kelajak uchun muhim»"),
        _("Yorliq, sarlavha, matn va pastdagi eslatma. Kartochkalar — «Kelajak "
          "uchun afzalliklar» bo'limida."),
        ("eyebrow", "title", "text", "note"),
    ),
    _s(
        "about.skills", "about",
        _("3. «Bola qanday ko'nikmalarni rivojlantiradi»"),
        _("Sarlavha. Ko'nikmalar ro'yxati — «Ko'nikmalar» bo'limida."),
        ("eyebrow", "title", "text"),
    ),
    _s(
        "about.demoday", "about",
        _("4. Demo Day — «Bola o'z loyihasini himoya qiladigan kun»"),
        _("Yorliq, sarlavha va matn. Raqamlar — «Loyiha himoyasi bosqichlari» "
          "bo'limida."),
        ("eyebrow", "title", "text"),
    ),
    _s(
        "about.school", "about",
        _("5. «MARS IT — bu oddiy kurslar emas»"),
        _("Yorliq, sarlavha va video tugmasi matni. Ro'yxat bandlari — «Maktab "
          "afzalliklari» bo'limida, videoning o'zi — «Sayt sozlamalari»da."),
        ("eyebrow", "title", "button_label"),
    ),
    _s(
        "about.founders", "about",
        _("6. «Maktab ortida kim turadi» — asoschilar"),
        _("Yorliq va sarlavha. Asoschilar — «Asoschilar» bo'limida."),
        ("eyebrow", "title"),
    ),
    _s(
        "about.teachers", "about",
        _("7. «IT sohasida ishlaydigan o'qituvchilar»"),
        _("Yorliq, sarlavha va matn. O'qituvchilar — «O'qituvchilar» bo'limida."),
        ("eyebrow", "title", "text"),
    ),

    # ------------------------------ Kurslar ------------------------------
    _s(
        "courses.hero", "courses",
        _("1. Hero — «Kurslar MARS IT School»"),
        _("Sahifa tepasidagi sarlavha, tugma matni va o'ngdagi rasm."),
        ("title", "button_label", "image"),
    ),
    _s(
        "courses.directions", "courses",
        _("2. «Yo'nalishlar» — IT Kids va IT dasturlash kartochkalari"),
        _("Bo'lim sarlavhasi va kartochkalar. Har bir kartochkada: nomi (sarlavha), "
          "qisqa izoh (yorliq), tavsif (matn), yosh (qiymat), rasm va havola."),
        ("title",),
        items=("title", "label", "text", "value", "image", "url", "icon_name"),
        item_name=_("Yo'nalish kartochkasi"),
        item_hint=_("«Texnologiyalar» — vergul bilan: html, css, js, react, python, cpp"),
    ),
    _s(
        "courses.coming_soon", "courses",
        _("3. «Tez orada...» banneri"),
        _("Yo'nalishlar ostidagi banner: sarlavha, matn va o'ngdagi astronavt "
          "rasmi. Rasm bo'sh qoldirilsa — maketdagi astronavt ishlatiladi."),
        ("title", "text", "image"),
    ),

    # ----------------------------- IT Kids -------------------------------
    _s(
        "itkids.hero", "itkids",
        _("1. Hero — «IT KIDS dasturlash»"),
        _("Sarlavha, tugmalar matni va o'ngdagi rasm."),
        ("title", "button_label", "button2_label", "image"),
    ),
    _s(
        "itkids.facts", "itkids",
        _("2. Ko'rsatkichlar tasmasi (yosh, davomiylik, format, guruh)"),
        _("Hero ostidagi to'rtta katak. Har birida: katta qiymat va uning ostidagi izoh."),
        (),
        items=("value", "label"),
        item_name=_("Ko'rsatkich"),
    ),
    _s(
        "itkids.about", "itkids",
        _("3. «Kurs haqida» — mavzular karuseli"),
        _("Yorliq, sarlavha, tavsif va aylanuvchi mavzu kartochkalari."),
        ("eyebrow", "title", "text", "note"),
        items=("title", "text", "icon_name", "icon"),
        item_name=_("Mavzu kartochkasi"),
        item_hint=_("Ikonka nomi: blocks, robot, wrench, chip, brain, code, rocket"),
    ),
    _s(
        "itkids.stages", "itkids",
        _("4. «O'qishning uch bosqichi» — akkordeon"),
        _("Sarlavha, izoh va bosqichlar. Har bir bosqichda: raqam (qiymat), "
          "nomi, davomiyligi (yorliq) va tavsifi."),
        ("eyebrow", "title", "text", "note"),
        items=("value", "title", "label", "text", "list", "note", "icon_name"),
        item_name=_("Bosqich"),
        item_hint=_("«Ro'yxat» — mavzular, har biri alohida qatorda. "
                    "«Natija» — bosqich yakunidagi ish. «Ikonka nomi» — "
                    "texnologiyalar vergul bilan: html, css, js, react, python, cpp."),
    ),
    _s(
        "itkids.gallery", "itkids",
        _("5. «Darslar muhiti» — galereya"),
        _("Sarlavha, izoh va rasmlar. Har bir rasmda tavsif (matn) — u ekranni "
          "o'qib beruvchi dasturlar uchun kerak."),
        ("eyebrow", "title", "text"),
        items=("image", "text"),
        item_name=_("Galereya rasmi"),
    ),

    # --------------------------- IT dasturlash ---------------------------
    _s(
        "itdev.hero", "itdev",
        _("1. Hero — «IT-dasturlash»"),
        _("Sarlavha, izoh, tugmalar matni va o'ngdagi rasm."),
        ("title", "text", "button_label", "button2_label", "image"),
    ),
    _s(
        "itdev.facts", "itdev",
        _("2. Ko'rsatkichlar tasmasi"),
        _("Hero ostidagi kataklar: katta qiymat va izoh."),
        (),
        items=("value", "label"),
        item_name=_("Ko'rsatkich"),
    ),
    _s(
        "itdev.about", "itdev",
        _("3. «Kurs haqida» — mavzular karuseli"),
        _("Yorliq, sarlavha, tavsif va mavzu kartochkalari."),
        ("eyebrow", "title", "text", "note"),
        items=("title", "text", "icon_name", "icon"),
        item_name=_("Mavzu kartochkasi"),
    ),
    _s(
        "itdev.stages", "itdev",
        _("4. «O'qish bosqichlari» — akkordeon"),
        _("Sarlavha, izoh va bosqichlar."),
        ("eyebrow", "title", "text", "note"),
        items=("value", "title", "label", "text", "list", "note", "icon_name"),
        item_name=_("Bosqich"),
        item_hint=_("«Ro'yxat» — mavzular, har biri alohida qatorda. "
                    "«Natija» — bosqich yakunidagi ish. «Ikonka nomi» — "
                    "texnologiyalar vergul bilan: html, css, js, react, python, cpp."),
    ),
    _s(
        "itdev.gallery", "itdev",
        _("5. «Darslar muhiti» — galereya"),
        _("Sarlavha, izoh va rasmlar."),
        ("eyebrow", "title", "text"),
        items=("image", "text"),
        item_name=_("Galereya rasmi"),
    ),

    # ------------------------------- SPACE -------------------------------
    _s(
        "space.hero", "space",
        _("1. Hero — «SPACE — o'ynab o'rgan»"),
        _("Sarlavha, tugma matni va o'ngdagi rasm."),
        ("title", "button_label", "image"),
    ),
    _s(
        "space.features", "space",
        _("2. «SPACE nimalarga qodir» — imkoniyatlar"),
        _("Yorliq, sarlavha, matn va imkoniyat kartochkalari."),
        ("eyebrow", "title", "text"),
        items=("title", "text", "icon_name"),
        item_name=_("Imkoniyat"),
        item_hint=_("Ikonka nomi: notes, book, code, feed, card, coins, cup, star"),
    ),
    _s(
        "space.gamification", "space",
        _("3. «O'qish — bu qiziqarli» (geymifikatsiya)"),
        _("Yorliq, sarlavha, matn va kartochkalar."),
        ("eyebrow", "title", "text"),
        items=("title", "text", "icon_name"),
        item_name=_("Geymifikatsiya kartochkasi"),
    ),
    _s(
        "space.premium", "space",
        _("4. «Space Premium»"),
        _("Yorliq, sarlavha, matn, eslatma va tugma. Ro'yxat bandlari — pastdagi "
          "elementlar."),
        ("eyebrow", "title", "text", "note", "button_label", "image"),
        items=("title", "text", "icon_name"),
        item_name=_("Premium imkoniyati"),
    ),
    _s(
        "space.shop", "space",
        _("5. «MARS Shop — ballarni sovg'aga almashtir»"),
        _("Yorliq, sarlavha, matn va tugma. Sovg'alar — pastdagi elementlar: "
          "nomi, koinlar soni (qiymat) va rasmi. «Qo'shimcha sarlavha» va "
          "«eslatma» — oxirgi katakdagi chaqiruv matni."),
        ("eyebrow", "title", "text", "subtitle", "note", "button_label"),
        items=("title", "value", "image"),
        item_name=_("Sovg'a"),
    ),
    _s(
        "space.parents", "space",
        _("6. «Ota-onalarga — bitta ilovada to'liq nazorat»"),
        _("Yorliq, sarlavha, matn va slaydlar. «Rasm» — barcha slaydlar uchun "
          "umumiy telefon rasmi; slaydning o'z rasmi yuklansa, u ustun turadi."),
        ("eyebrow", "title", "text", "image"),
        items=("title", "text", "image"),
        item_name=_("Slayd"),
        item_hint=_("«Rasm» — shu slayd uchun telefon rasmi. Bo'sh qoldirilsa, "
                    "blokning umumiy rasmi ishlatiladi."),
    ),
    _s(
        "space.application", "space",
        _("7. «SPACE ko'magida o'qishni boshlang» — ariza"),
        _("Yorliq, sarlavha va matn."),
        ("eyebrow", "title", "text"),
    ),

    # ---------------------------- Yangiliklar ----------------------------
    _s(
        "news.hero", "news",
        _("1. Hero — «MARS IT maktabi hayoti»"),
        _("Sahifa tepasidagi sarlavha, izoh va rasm."),
        ("title", "text", "image"),
    ),
    _s(
        "news.list", "news",
        _("2. Yangiliklar ro'yxati — sarlavha"),
        _("Ro'yxat tepasidagi yorliq va sarlavha, hamda ro'yxat bo'sh bo'lgandagi matn."),
        ("eyebrow", "title", "subtitle", "note"),
    ),

    # ----------------------------- Kontaktlar ----------------------------
    _s(
        "contacts.hero", "contacts",
        _("1. Hero — «Doim aloqada»"),
        _("Sahifa tepasidagi sarlavha va rasm."),
        ("title", "button_label", "image"),
    ),
    _s(
        "contacts.info", "contacts",
        _("2. Kontaktlar bloki"),
        _("Yorliq, sarlavha va matn. Telefon, email va ish vaqti — «Sayt "
          "sozlamalari»dan olinadi."),
        ("eyebrow", "title", "text"),
    ),
    _s(
        "contacts.branches", "contacts",
        _("3. «Toshkentdagi maktab manzillari» — xarita va ro'yxat"),
        _("Yorliq, sarlavha va izoh. Filiallar — «Filiallar» bo'limida."),
        ("eyebrow", "title", "text", "note"),
    ),
    _s(
        "contacts.trial", "contacts",
        _("4. «Sinov darsiga yoziling» — shu sahifadagi variant"),
        _("Kontaktlar sahifasidagi ariza blokining sarlavhasi va izohi."),
        ("title", "text"),
    ),

    # ---------------------------- Vakansiyalar ---------------------------
    _s(
        "vacancies.hero", "vacancies",
        _("1. Hero — «MARS IT School'da ishlash»"),
        _("Sahifa tepasidagi sarlavha, izoh va rasm."),
        ("title", "text", "image"),
    ),
    _s(
        "vacancies.list", "vacancies",
        _("2. Vakansiyalar ro'yxati — sarlavha"),
        _("Yorliq, sarlavha, matn va ro'yxat bo'sh bo'lgandagi yozuv."),
        ("eyebrow", "title", "text", "subtitle", "note"),
    ),

    # -------------------------------- Test -------------------------------
    _s(
        "quiz.intro", "quiz",
        _("1. Test boshlanishi — salomlashuv va izoh"),
        _("«Salom, bo'lajak dasturchi!» sarlavhasi va uning ostidagi matn."),
        ("title", "subtitle", "text"),
        hideable=False,
    ),
    _s(
        "quiz.contact", "quiz",
        _("2. «Deyarli tayyor!» — kontakt qadami"),
        _("Test oxiridagi kontakt so'raladigan qadam matni va tugmasi."),
        ("title", "text", "button_label"),
        hideable=False,
    ),
    _s(
        "quiz.result", "quiz",
        _("3. Natija sahifasi — sarlavhalar"),
        _("«Natijangiz tayyor!» sarlavhasi va ko'nikmalar bo'limi yorliqlari."),
        ("title", "eyebrow", "subtitle", "text"),
        hideable=False,
    ),

    # ------------------------------- Umumiy ------------------------------
    _s(
        "common.trial", "common",
        _("«Bepul sinov darsi» — ariza bloki (barcha sahifalarda)"),
        _("Yorliq, sarlavha va izoh. Kontaktlar sahifasida o'z varianti bor."),
        ("eyebrow", "title", "text"),
        hideable=False,
    ),
    _s(
        "common.buttons", "common",
        _("Takrorlanadigan tugmalar matni"),
        _("«Bepul sinov darsiga yozilish» va «Kurslarni ko'rish» tugmalari — "
          "sayt bo'ylab bir xil."),
        ("button_label", "button2_label"),
        hideable=False,
    ),
    _s(
        "common.footer", "common",
        _("Sayt podvali (futer)"),
        _("Podvaldagi qisqa matn va mualliflik yozuvi. Telefon, ijtimoiy tarmoqlar — "
          "«Sayt sozlamalari»da."),
        ("text", "note"),
        hideable=False,
    ),
]

#: kalit → bo'lim tavsifi
SECTION_INDEX: dict[str, dict] = {section["key"]: section for section in SECTIONS}

#: sahifa kaliti → shu sahifadagi bo'limlar (sayt tartibida)
SECTIONS_BY_PAGE: dict[str, list[dict]] = {}
for _section in SECTIONS:
    SECTIONS_BY_PAGE.setdefault(_section["page"], []).append(_section)

#: kalit → tartib raqami (saytdagi joylashuvi)
SECTION_ORDER: dict[str, int] = {
    section["key"]: index for index, section in enumerate(SECTIONS)
}
