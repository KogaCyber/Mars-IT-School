# Sayt va admin panel sekinligi — sabablari va tuzatishlar

## O'lchov (tuzatishdan oldin)

Railway'dagi backendga to'g'ridan-to'g'ri so'rovlar:

| So'rov | TTFB |
|---|---|
| `/health/` (bitta Mongo `ping`) | 0.91–1.15 s |
| `/api/v1/teachers/` | 1.62 s |
| `/api/v1/news/` | 1.11 s |
| `/static/admin/css/base.css` (bazaga tegmaydi) | 0.75 s |
| mavjud bo'lmagan manzil, 404 (bazaga tegmaydi) | 0.75–0.92 s |

Bosh sahifa 6 ta shunday so'rov yuborardi.

## Sabablari

### 1. MongoDB Singapurda, backend Yevropada — ENG KATTA SABAB

```
Atlas klaster hosti:  mtm-aws-apsoutheast1-1-m0-24.mjeur.mongodb.net
                      └─ AWS ap-southeast-1 = Singapur, M0 = bepul tarif
Railway edge:         ams1 = Amsterdam
```

Har bir MongoDB so'rovi Yevropa ↔ Singapur oralig'ini bosib o'tadi — bu ~150–170 ms,
faqat tarmoq uchun. Admin panelning bitta sahifasi 5–7 ta so'rov qiladi, ya'ni
**bir sahifa uchun ~1 soniya sof kutish**. Ustiga M0 bepul tarif umumiy
protsessorda ishlaydi va yuk bo'lganda sekinlashadi.

**Bu kod bilan tuzatilmaydi.** Quyidagi ikkitadan biri kerak (pastdagi
«Qolgan ishlar» bo'limiga qarang).

### 2. Hech qanday keshlash yo'q edi

Sayt kontenti (kurslar, FAQ, o'qituvchilar) deyarli o'zgarmaydi, lekin har bir
tashrifchi uchun MongoDB'dan qaytadan o'qilardi.

### 3. Bosh sahifa 6 ta alohida so'rov yuborardi

Har biri ~1 soniya. Gunicorn esa `--workers 3` sync rejimda edi: sync worker bir
vaqtda faqat bitta so'rovni bajaradi, qolganlari navbatda turadi.

### 4. Rasmlar 60 soniyaga keshlanardi

WhiteNoise standarti `max-age=60`. Ya'ni brauzer deyarli har sahifada barcha
rasmlarni Railway'dan qayta yuklab olardi (har biri ~0.8 s).

### 5. Frontend'da 5.5 MB siqilmagan PNG

`src/assets/images/` — 580×580 o'lchamdagi rasmlar 400–550 KB dan edi.

### 6. Leaflet (xarita, 150 KB) har bir sahifada yuklanardi

`manualChunks` barcha kutubxonalarni bitta `vendor` bo'lagiga qo'yardi, xarita
esa faqat «Kontaktlar» sahifasida kerak.

## Qilingan tuzatishlar

### Backend

| Fayl | O'zgarish |
|---|---|
| `apps/core/cache.py` (yangi) | Ochiq API javoblari serverda keshlanadi va `Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=600` bilan brauzer/CDN'ga beriladi. Kesh kaliti ichida til bor (`?lang=` va `Accept-Language`), shuning uchun tillar aralashib ketmaydi. |
| `apps/core/views.py` | Yangi `/api/v1/home/` — bosh sahifaning butun kontenti bitta javobda. |
| Barcha ochiq viewset'lar | `PublicCacheMixin` qo'shildi. **Istisnolar:** yangilik sahifasi (`retrieve` ko'rishlar sonini oshiradi) va test (`quizzes/` har safar tasodifiy savollar beradi) — ular ataylab keshlanmaydi. |
| `config/wsgi.py` | Media fayllar `max-age=60` o'rniga bir yilga keshlanadi. Django yuklangan fayl nomiga tasodifiy qo'shimcha qo'shgani uchun (`teacher-1_eD5NUKe.webp`) bu xavfsiz. |
| `config/settings/base.py` | `GZipMiddleware`; statik fayllar uchun `WHITENOISE_MAX_AGE`; `PUBLIC_CACHE_SECONDS`; admin sessiyasi uchun `SESSION_ENGINE = cached_db` (har so'rovda bitta Mongo o'qishi kamayadi). |
| `apps/core/apps.py` | Admin uchun `show_full_result_count = False` (har ro'yxat sahifasida ortiqcha `count()` yuborilmaydi) va `list_per_page = 25` (standart 100 o'rniga). |
| `railway.json` | `--worker-class gthread --workers 2 --threads 8 --preload --keep-alive 15`. Sync worker bir vaqtda bitta so'rovni bajaradi; ish esa deyarli butunlay MongoDB javobini kutish, shuning uchun thread'lar buni parallel qiladi (bir vaqtda 16 so'rov). |

### Frontend

| Fayl | O'zgarish |
|---|---|
| `src/assets/images/*` | 26 ta PNG → WebP: **5.46 MB → 0.71 MB** (87% kam). |
| `src/views/HomeView.vue` | 5 ta so'rov o'rniga bitta `/api/v1/home/`. |
| `vite.config.js` | Leaflet alohida bo'lakka chiqarildi: `vendor` 376 KB → 227 KB (gzip 130 → 83 KB). |
| `index.html` | Backend domeniga `preconnect` — birinchi so'rovdan DNS + TCP + TLS vaqti (~0.25 s) olib tashlanadi. |

**Natija (mahalliy o'lchov):** keshdan kelgan javob 1.16 s → 0.007 s.

## Qolgan ishlar (kod emas, infratuzilma)

Yuqoridagi 1-sabab hali kuchda. Ikkita yo'l bor, birinchisi afzal:

1. **MongoDB Atlas klasterini Railway yoniga ko'chirish.** Atlas → klaster →
   yangi klaster Yevropa regionida (masalan AWS `eu-central-1` yoki
   `eu-west-1`), keyin `mongodump` / `mongorestore` bilan ma'lumot ko'chiriladi
   va `MONGODB_URI` yangilanadi. Har bir so'rovdan ~150 ms yo'qoladi.
2. Yoki Railway xizmatini Singapur regioniga ko'chirish — lekin unda sayt
   Toshkentdagi foydalanuvchilarga uzoqroq bo'ladi, shuning uchun 1-variant
   yaxshiroq.

Qo'shimcha:

* **Atlas M0 → M10.** Bepul tarif umumiy protsessorda ishlaydi va yuk paytida
  sezilarli sekinlashadi.
* **Redis qo'shish** (Railway plugin, `REDIS_URL`). Hozir kesh `LocMemCache` —
  har bir worker o'z keshini saqlaydi. Redis bilan kesh barcha worker'lar uchun
  umumiy bo'ladi va samaradorligi oshadi.
* **Media fayllarni CDN'ga** (masalan Cloudflare R2 yoki S3 + CDN). Hozir
  rasmlarni Railway'dagi gunicorn uzatadi.
