# Sayt kontenti va admin panel

Admin panel sayt **sahifalari** bo'yicha tuzilgan. Chap menyudagi har bir guruh —
saytning bitta sahifasi, uning ichida esa o'sha sahifadagi bloklar **saytdagi
tartibda** turadi:

```
Bosh sahifa
  └── Bosh sahifa bo'limlari
        1. Hero — sarlavha, matn, tugmalar, astronavt rasmi
        2. «Nega MARS IT School ni tanlashadi» — sarlavha
        3. SPACE platformasi bloki
        …
  └── Afzalliklar (kartochkalar)
  └── Ota-onalar fikri
  └── Savol-javoblar
```

Bo'limni ochganda faqat o'sha blokka tegishli maydonlar ko'rinadi: sarlavha,
matn, tugma matni, rasm va (kerak bo'lsa) kartochkalar ro'yxati. Ruscha matn
asosiy blokda, o'zbekcha va inglizcha tarjimalar — pastdagi yig'ma bloklarda.

## Nima qayerda saqlanadi

| Nima | Qayerda |
| --- | --- |
| Bloklar ro'yxati (qaysi sahifada, qanday tartibda, qaysi maydonlar) | `apps/core/sections.py` |
| Bloklar kontenti (matn, rasm, kartochkalar) | `PageSection` va `SectionItem` modellari |
| Admin paneldagi ko'rinish | `apps/core/section_admin.py` |
| Sahifalar bo'yicha menyu | `apps/core/admin_site.py` |
| Saytga beriladigan API | `GET /api/v1/content/` (bosh sahifa uchun `/api/v1/home/` ichida ham) |
| Maketdagi standart matnlar (urug') | `apps/core/fixtures/section_defaults.json` |

**Bo'sh maydon — xato emas.** Sayt bo'sh qiymat o'rniga maketdagi (frontenddagi
`i18n/messages` yoki `data/*.js`) matnni ko'rsatadi, rasm yuklanmagan bo'lsa —
loyihadagi rasmni. Ya'ni bo'lim hech qachon bo'sh ko'rinmaydi.

## Bo'limlarni bazaga yozish

```bash
python manage.py sync_sections
```

Buyruq reestrda bor, lekin bazada yo'q bo'limlarni yaratadi (va birinchi
marta maketdagi matn bilan to'ldiradi), mavjudlarining tartibini yangilaydi.
Hech narsani o'chirmaydi. Railway'da u har bir deploy'da `migrate`dan keyin
avtomatik ishlaydi (`railway.json`). Bundan tashqari, bo'limlar ro'yxati admin
panelda ochilganda ham jimgina tekshiriladi — yangi blok darrov ko'rinadi.

## Yangi blok qo'shish

1. `apps/core/sections.py` ga bo'lim qo'shing: kalit (`home.hero` kabi),
   sahifa, nomi, izohi va qaysi maydonlar tahrirlanishi.
2. Saytdagi komponentda o'qing:

   ```js
   const section = useSection('home.hero', { title: 'home.heroTitle' })
   ```

   Ikkinchi argument — maketdagi tarjima kalitlari (zaxira matn).
3. Kerak bo'lsa maketdagi joriy matnni urug' faylga chiqaring:

   ```bash
   cd frontend && npx vite-node scripts/export-sections.mjs
   ```
4. `python manage.py sync_sections`.
