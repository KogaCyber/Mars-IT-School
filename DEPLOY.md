# Mars IT School — serverga yuklash qo'llanmasi

Loyiha ikki qismdan iborat va ular **alohida** joylashtiriladi:

| Qism | Nima | Tavsiya etilgan xizmat |
| --- | --- | --- |
| `backend/` | Django REST API + admin panel | Railway (`railway.json` tayyor) |
| `frontend/` | Vue 3 SPA + prerender qilingan HTML | Vercel (`vercel.json` tayyor) |
| Ma'lumotlar bazasi | MongoDB | MongoDB Atlas |

---

## 1. MongoDB Atlas

1. Bepul M0 klaster yarating (region: Frankfurt yoki Mumbai — Toshkentga eng yaqini).
2. **Database Access** → foydalanuvchi qo'shing (kuchli parol).
3. **Network Access** → Railway chiquvchi IP'lari oldindan ma'lum emas, shuning uchun
   `0.0.0.0/0` qo'yiladi. Himoya parol va TLS orqali ta'minlanadi.
4. Ulanish satrini oling:
   `mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/mars_it_school?retryWrites=true&w=majority`

---

## 2. Backend — Railway

### 2.1 Maxfiy kalitlarni yarating

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"   # DJANGO_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"   # JWT_SIGNING_KEY
```

### 2.2 Railway → Variables

```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
DJANGO_SECRET_KEY=<yuqorida yaratilgan kalit>
JWT_SIGNING_KEY=<ikkinchi kalit>

ALLOWED_HOSTS=mars-it-school-production.up.railway.app
CORS_ALLOWED_ORIGINS=https://mars-it-school-lemon.vercel.app
CSRF_TRUSTED_ORIGINS=https://mars-it-school-lemon.vercel.app
FRONTEND_URL=https://mars-it-school-lemon.vercel.app

MONGODB_URI=mongodb+srv://...
MONGODB_NAME=mars_it_school

# Admin panel manzilini ALBATTA o'zgartiring — /admin/ ni botlar kuniga
# minglab marta uradi.
ADMIN_URL=mars-panel-7fa2/

NUM_PROXIES=1

# Ikkala papka ham DOIMIY volume'da bo'lishi shart (Railway → Volumes).
# Konteyner diski har deploy'da tozalanadi.
MEDIA_ROOT=/data/media
# Nomzodlar rezyumesi — SHAXSIY MA'LUMOT. Bu papka MEDIA_ROOT ichida
# BO'LMASLIGI kerak: WhiteNoise butun MEDIA_ROOT ni ochiq uzatadi, ya'ni
# u yerdagi fayl manzilini bilgan har kim yuklab olardi.
PRIVATE_MEDIA_ROOT=/data/private-media

REDIS_URL=<Railway Redis plugin URL>

# Saytda ro'yxatdan o'tish sahifasi yo'q — manzil yopiq turadi.
# O'quvchi kabineti qo'shilgandagina True qiling.
PUBLIC_REGISTRATION_ENABLED=False

EMAIL_HOST=smtp.yandex.com
EMAIL_PORT=587
EMAIL_HOST_USER=no-reply@marsitschool.uz
EMAIL_HOST_PASSWORD=<smtp paroli>
LEAD_NOTIFY_EMAILS=info@marsitschool.uz
ADMIN_EMAILS=info@marsitschool.uz

TELEGRAM_BOT_TOKEN=<ixtiyoriy>
TELEGRAM_CHAT_ID=<ixtiyoriy>
```

> `config.settings.production` xato sozlamalar bilan ishga tushmaydi:
> `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` bo'sh bo'lsa yoki `DJANGO_SECRET_KEY`
> standart qiymatda qolsa deploy darrov to'xtaydi. Bu jimgina buzilgan saytdan afzal.

### 2.3 Volume (yuklanadigan rasmlar uchun — majburiy)

Railway konteyner diski **vaqtinchalik**: har deploy'da admin paneldan yuklangan
o'qituvchi rasmlari, yangilik muqovalari va rezyumelar yo'qoladi.

Railway → **Volumes** → yangi volume, mount path `/data`.
So'ng `MEDIA_ROOT=/data/media` qiling (yuqorida bor).

### 2.4 Birinchi deploy'dan keyin

```bash
railway run python manage.py createsuperuser
```

Tekshirish: `https://<domen>/health/` → `{"status":"ok","database":true}`.

### 2.5 Admin panelni alohida portga chiqarish (ixtiyoriy, xavfsizroq)

Ikkita Railway xizmati bitta repodan ishlaydi:

* API xizmati: `SERVICE_ROLE=api` — bu portda admin panel umuman mavjud emas;
* Admin xizmati: `SERVICE_ROLE=admin` — faqat maktab xodimlari uchun, ochiq
  internetdan yopib qo'yish mumkin.

---

## 3. Frontend — Vercel

### 3.1 Sozlamalar

* Root Directory: `frontend`
* Framework: Vite (avtomatik aniqlanadi)
* Build/Install buyruqlari `vercel.json` da yozilgan.

### 3.2 Environment Variables

Bu qiymatlar `frontend/.env.production` faylida git'ga qo'shilgan, shuning uchun
Vercel'da qo'lda hech narsa qo'yish shart emas — build ularni fayldan oladi:

```
VITE_API_BASE_URL=https://mars-it-school-production.up.railway.app
VITE_SITE_URL=https://mars-it-school-lemon.vercel.app
```

`VITE_` prefiksli qiymatlar build vaqtida bundle ichiga yoziladi — ular baribir
ommaviy, shuning uchun git'da turishi xavfsiz. Maxfiy qiymatlarni bu faylga
yozmang. Vercel dashboard'ida xuddi shu nomlar qo'yilsa, ular fayldan ustun turadi.

> `VITE_SITE_URL` ni to'g'ri yozish **shart**: `sitemap.xml`, `llms.txt`,
> canonical va hreflang havolalari aynan shu manzildan yasaladi. `localhost`
> qolib ketsa qidiruv tizimlari noto'g'ri manzilni indekslaydi.

**Vercel dashboard'ida qo'shimcha bitta o'zgaruvchi qo'ying:**

```
SEO_STRICT=1
```

`sitemap.xml` dagi kurs, yangilik, filial va vakansiya sahifalari build vaqtida
backend'dan olinadi. Backend javob bermasa, sitemap FAQAT statik sahifalardan
iborat bo'lib qoladi va butun katalog Google uchun ko'rinmay ketadi — build esa
muvaffaqiyatli tugagani uchun buni hech kim sezmaydi.

`SEO_STRICT=1` shu holatda build'ni to'xtatadi: Vercel eski, to'liq versiyani
saytda qoldiradi va deploy qizil bo'lib ko'rinadi. Lokalda va CI'da backend
bo'lmasligi normal, shuning uchun u yerda bu o'zgaruvchi qo'yilmaydi — faqat
ogohlantirish chiqadi.

### 3.3 Backend domenini CSP ga qo'shing

`frontend/vercel.json` → `Content-Security-Policy` → `connect-src`.
Hozir `https://api.marsitschool.uz` va `https://*.up.railway.app` ruxsat etilgan
(Railway domeni ikkinchi qolip ostiga tushadi).
Backend boshqa domenda bo'lsa, o'sha domenni shu yerga qo'shing — aks holda
brauzer API so'rovlarini bloklaydi.

### 3.4 Build nima qiladi

`npm run build` = `vite build` + `scripts/generate-seo.mjs`. Ikkinchi bosqich
backenddan kurslar, yangiliklar, filiallar, vakansiyalar va FAQ'ni olib:

* `sitemap.xml` — barcha sahifalar, hreflang va rasmlar bilan;
* `llms.txt` — javob beruvchi tizimlar uchun faktik ma'lumot va savol-javoblar;
* har bir sahifa uchun alohida statik HTML — meta-teglar, canonical va JSON-LD
  HTML ichida bo'ladi, shuning uchun JS ishlatmaydigan crawler ham hammasini ko'radi.

Backend javob bermasa build to'xtamaydi — faqat statik qism yaratiladi.
**Shuning uchun backendni frontenddan oldin ishga tushiring**, aks holda birinchi
build'da kurs va yangilik sahifalari sitemap'ga tushmay qoladi.

---

## 4. Domen va DNS

```
marsitschool.uz       → CNAME → cname.vercel-dns.com
www.marsitschool.uz   → CNAME → cname.vercel-dns.com
api.marsitschool.uz   → CNAME → <loyiha>.up.railway.app
```

`www` ni asosiy domenga 301 bilan yo'naltiring (Vercel → Domains → Redirect),
shunda bitta sahifa ikki manzilda indekslanmaydi.

---

## 5. Deploy'dan keyingi ro'yxat

```bash
# Backend
curl https://api.marsitschool.uz/health/            # {"status":"ok"}
curl -I https://api.marsitschool.uz/api/v1/courses/ # 200 + xavfsizlik sarlavhalari
curl -I http://api.marsitschool.uz/api/v1/courses/  # 301 → https

# Frontend
curl -s https://marsitschool.uz/robots.txt | head
curl -s https://marsitschool.uz/sitemap.xml | head
curl -s https://marsitschool.uz/llms.txt | head
curl -s https://marsitschool.uz/kursy | grep -o '<link rel="canonical"[^>]*>'
```

- [ ] `/admin/` 404 qaytaradi (manzil o'zgartirilgan)
- [ ] Superuser yaratilgan, admin panelga kirish ishlaydi
- [ ] Ariza formasi ishlaydi, email/Telegram xabari keladi
- [ ] Google Search Console'ga `sitemap.xml` yuborilgan
- [ ] Yandex Webmaster'ga sayt qo'shilgan (O'zbekistonda ulushi katta)
- [ ] Google Business Profile — har bir filial uchun alohida karta
- [ ] Rich Results Test: bosh sahifa, kurs sahifasi, vakansiya sahifasi

---

## 6. Muntazam xizmat ko'rsatish

* **Kontent yangilangach frontendni qayta build qiling.** Prerender qilingan HTML
  va `sitemap.xml` build vaqtida yasaladi, shuning uchun admin paneldan yangi kurs
  yoki yangilik qo'shilsa, Vercel'da Redeploy bosiladi (yoki Deploy Hook'ni
  haftalik cron'ga ulang).
* Bog'liqliklarni har chorakda yangilang: `pip list --outdated`, `npm outdated`.
* Atlas'da avtomatik zaxira nusxa (backup) yoqilganini tekshiring.

---

## 7. Tez-tez uchraydigan nosozliklar

### `502 Application failed to respond` va `x-railway-fallback: true`

```bash
curl -i https://<domen>/health/
# HTTP/2 502 ... x-railway-fallback: true
```

Bu sarlavha — so'rov konteynerga **umuman yetib bormaganini** bildiradi: javobni
Railway'ning zaxira sahifasi qaytaryapti. Django loglarida traceback bo'lmasligi
va gunicorn'ning `Listening at: http://0.0.0.0:8080` deb yozishi buni tasdiqlaydi.

Tekshirish tartibi:

1. **Deploy loglarida request bormi?** `railway.json` da `--access-logfile -` bor,
   ya'ni har bir so'rov logga tushishi kerak. Railway'ning o'z healthcheck'i ham
   ko'rinmasa — muammo marshrutlashda, Django'da emas.
2. **Domenning target port'i.** Settings → Networking → Public Networking →
   domen yonidagi port gunicorn tinglayotgan port bilan bir xil bo'lsin.
   Mos kelmasa domenni o'chirib qaytadan yarating.
3. **Variables'da qo'lda qo'yilgan `PORT` bo'lmasin.** Uni Railway o'zi inject
   qiladi va domen mapping'ini shunga qarab quradi; qo'lda qo'yilgani ikkalasini
   uzib qo'yadi.
4. **Deployment holati `Active` mi?** `Failed healthcheck` bo'lsa Railway o'sha
   deploy'ni jonli trafikka ulamaydi va aynan shu 502 ni qaytaradi.

### Frontend backendga ulanmayapti

Avval yuqoridagi `curl https://<backend>/health/` ni ishga tushiring. `502` yoki
`000` qaytsa — muammo backendda, CORS'da emas. `200` qaytsa-yu brauzerda xato
bo'lsa, DevTools → Network → Console'dagi xabarga qarang:

* `CORS policy` — Railway'da `CORS_ALLOWED_ORIGINS` da frontend domeni yo'q.
* `Refused to connect ... Content Security Policy` — `vercel.json` dagi
  `connect-src` ga backend domenini qo'shing (§3.3).
* So'rovlar Vercel domeniga ketyapti — build'da `VITE_API_BASE_URL` bo'sh qolgan.
  Vite bu qiymatni **build vaqtida** bundle ichiga yozadi, shuning uchun
  o'zgartirgandan keyin Redeploy qilish shart.

---

## Xavfsizlik bo'yicha majburiy qadamlar

### Rezyume fayllarini ko'chirish (bir marta)

Yangilanishdan oldin yuklangan rezyumelar hali ham ochiq `MEDIA_ROOT/resumes/`
ichida yotadi va `/media/resumes/...` manzilida hammaga ko'rinadi. Ularni
himoyalangan papkaga ko'chiring:

```bash
# Avval nima ko'chishini ko'rib oling
python manage.py move_resumes_private --dry-run

# Keyin haqiqiy ko'chirish
python manage.py move_resumes_private
```

Railway'da bu `railway run` orqali bajariladi. Ko'chirishdan keyin eski
`/media/resumes/...` manzillari 404 qaytaradi — bu kutilgan natija. Fayl endi
admin paneldagi «Rezyume» havolasi orqali, xodim huquqi bilan ochiladi.

### Tekshiruv ro'yxati (deploy'dan keyin)

| Tekshiruv | Kutilgan natija |
| --- | --- |
| `curl -I <domen>/media/resumes/<eski-fayl>` | `404` |
| Admin panelda «Vakansiya arizasi» → «Rezyume» havolasi | fayl yuklanadi |
| Chiqib turib o'sha havolani ochish | `403` |
| `curl <domen>/api/v1/quiz-results/abc/` | `404` (`500` emas) |
| Bosh sahifada video tugmasi | rolik modal ichida o'ynaydi |
| `curl <domen>/robots.txt \| grep Sitemap` | domen sayt domeni bilan bir xil |
| `python manage.py check --deploy` | 0 muammo |

### Muhit o'zgaruvchilari — xavfsizlik uchun eng muhimlari

| O'zgaruvchi | Nega muhim |
| --- | --- |
| `PRIVATE_MEDIA_ROOT` | Qo'yilmasa rezyumelar har deploy'da yo'qoladi (jarayon boshlanishida ogohlantirish chiqadi). |
| `ADMIN_URL` | `/admin/` da qolsa botlar kuniga minglab marta uradi. |
| `PUBLIC_REGISTRATION_ENABLED` | `True` bo'lsa istalgan odam hisob ocha oladi. |
| `NUM_PROXIES` | Noto'g'ri bo'lsa so'rov cheklovi va IP aniqlash aylanib o'tiladi. |
| `LEAD_THROTTLE_RATE` | Juda past qiymat CGNAT ortidagi haqiqiy mijozlarni bloklaydi. |
