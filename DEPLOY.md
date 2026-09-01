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

ALLOWED_HOSTS=api.marsitschool.uz,<loyiha>.up.railway.app
CORS_ALLOWED_ORIGINS=https://marsitschool.uz,https://www.marsitschool.uz
CSRF_TRUSTED_ORIGINS=https://marsitschool.uz,https://api.marsitschool.uz
FRONTEND_URL=https://marsitschool.uz

MONGODB_URI=mongodb+srv://...
MONGODB_NAME=mars_it_school

# Admin panel manzilini ALBATTA o'zgartiring — /admin/ ni botlar kuniga
# minglab marta uradi.
ADMIN_URL=mars-panel-7fa2/

NUM_PROXIES=1
MEDIA_ROOT=/data/media
REDIS_URL=<Railway Redis plugin URL>

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

```
VITE_API_BASE_URL=https://api.marsitschool.uz
VITE_SITE_URL=https://marsitschool.uz
```

> `VITE_SITE_URL` ni to'g'ri yozish **shart**: `sitemap.xml`, `llms.txt`,
> canonical va hreflang havolalari aynan shu manzildan yasaladi. `localhost`
> qolib ketsa qidiruv tizimlari noto'g'ri manzilni indekslaydi.

### 3.3 Backend domenini CSP ga qo'shing

`frontend/vercel.json` → `Content-Security-Policy` → `connect-src`.
Hozir `https://api.marsitschool.uz` va `https://*.up.railway.app` ruxsat etilgan.
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
