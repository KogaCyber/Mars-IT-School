# Xavfsizlik siyosati

## Zaiflik topsangiz

Zaiflikni **ommaviy issue sifatida ochmang**. Uni to'g'ridan-to'g'ri yuboring:
**security@marsitschool.uz**

Xabarga quyidagilarni qo'shing:

- zaiflik turi va qaysi manzil/komponentga tegishli ekani;
- qadamma-qadam takrorlash yo'li (so'rov namunasi bo'lsa yaxshi);
- ta'sir doirasi — nima olinishi yoki o'zgartirilishi mumkin.

Javob berish muddati: **72 soat ichida** tasdiqlash, **14 kun ichida** tuzatish
rejasi. Tuzatilgandan keyin, agar xohlasangiz, hurmat ro'yxatida
(`acknowledgements`) ismingizni ko'rsatamiz.

**Iltimos qilmang:** DoS/yuklama testlari, spam yuborish, boshqa
foydalanuvchilarning ma'lumotlariga kirish, ijtimoiy muhandislik.

---

## Himoya qavatlari

Bu bo'lim tekshiruvchilar uchun: qaysi hujum turiga qanday himoya qo'yilgan
va u kodning qayerida.

### Autentifikatsiya va sessiyalar

| Himoya | Qayerda |
|---|---|
| Argon2 parol hasher (Django tavsiyasi) | `config/settings/base.py` → `PASSWORD_HASHERS` |
| Minimal parol uzunligi — 10 belgi + 3 ta validator | `AUTH_PASSWORD_VALIDATORS` |
| Brute-force cheklovi: 5 urinish → 30 daqiqa blok, IP **va** login bo'yicha | `django-axes`, `AXES_*` |
| Proksi ortida haqiqiy IP (soxta `X-Forwarded-For` ishlamaydi) | `AXES_IPWARE_PROXY_COUNT`, `apps/leads/utils.py` |
| Timing-attack: mavjud bo'lmagan foydalanuvchi uchun ham hash hisoblanadi | `apps/accounts/backends.py` |
| JWT access — 15 daqiqa, refresh — 7 kun, rotatsiya bilan | `SIMPLE_JWT` |
| Chiqishda va rotatsiyada eski refresh token bekor qilinadi | `apps/accounts/tokens.py` |
| **Parol o'zgarganda barcha tokenlar** (jumladan o'g'irlangan, bizga noma'lum) darhol yaroqsiz — `epoch` da'vosi | `apps/accounts/authentication.py` |
| Ro'yxatdan o'tish standart bo'yicha yopiq | `PUBLIC_REGISTRATION_ENABLED=False` |

### Shaxsiy ma'lumotlar

| Himoya | Qayerda |
|---|---|
| Rezyume `MEDIA_ROOT` dan **tashqarida** — statik uzatuvchi ko'rmaydi | `apps/core/storage.py`, `PRIVATE_MEDIA_ROOT` |
| Ikki papka bir-birining ichida bo'lsa — ishga tushmaydi | `config/settings/base.py` (ishga tushish tekshiruvi) |
| `.url` chaqirilsa ochiq xatolik — tasodifiy havola chiqib ketmaydi | `PrivateMediaStorage.url()` |
| Fayl nomi tasodifiy — nomzod ismi diskda ham, sarlavhada ham yo'q | `apps/core/uploads.py` |
| Yuklab olish faqat xodimga; kirmagan ham, begona ham bir xil **403** | `apps/core/views.py:staff_required` |
| Har bir yuklab olish **qayd etiladi** (kim, kimnikini, qaysi IP dan) | `security.audit` loggeri |
| Test natijasi javobida ism/telefon umuman yo'q | `apps/quiz/serializers.py` |

### Kirish nazorati

| Himoya | Qayerda |
|---|---|
| Ommaviy API faqat **o'qiydi** (`GET/HEAD/POST/OPTIONS`) | `CORS_ALLOW_METHODS` |
| Yozadigan uchta manzil: ariza, vakansiya arizasi, test topshirish | — |
| Test natijasi havolasi — 256 bitlik tasodifiy kalit, ObjectId emas (IDOR yopiq) | `Submission.public_token` |
| Admin panel maxfiy manzilda + ixtiyoriy IP oq ro'yxati | `ADMIN_URL`, `ADMIN_ALLOWED_IPS` |
| Ruxsatsiz IP **404** oladi (403 emas — manzil borligini tasdiqlamaydi) | `apps/core/middleware.py` |
| API hujjatlari (`/api/docs/`) xodim huquqi ortida | `config/urls.py` |
| Admin panel va API alohida jarayonlarda ishlashi mumkin | `SERVICE_ROLE` |

### Kiruvchi ma'lumot

| Himoya | Qayerda |
|---|---|
| MongoDB `icontains` regexga aylanadi — qidiruv matni escape qilinadi (ReDoS/xato) | `apps/core/filters.py` |
| Yuklangan fayl **mazmuni** tekshiriladi (magic bytes), kengaytmaning o'zi yetarli emas | `apps/core/uploads.py` |
| Fayl hajmi 5 MB, avatar 2 MB, form maydonlari 500 ta | `DATA_UPLOAD_MAX_*` |
| Telefon, yosh, ism — server tomonda qayta tekshiriladi | serializerlar |
| Email sarlavhasiga qator qo'shib bo'lmaydi (header injection) | `apps/leads/services.py:_safe_subject` |
| Noto'g'ri ObjectId → 400/404, hech qachon 500 emas | `apps/core/exceptions.py` |
| Xatolik javobida stack trace, SQL yoki fayl yo'llari yo'q | `api_exception_handler` |

### Tarmoq va sarlavhalar

| Himoya | Qayerda |
|---|---|
| **SSRF:** domen oq ro'yxati + DNS orqali IP tekshiruvi + **har bir redirect qayta tekshiriladi** | `apps/core/net.py` |
| Ichki manzillar rad etiladi: loopback, 10/8, 192.168/16, **169.254/16 (metadata)**, CGNAT, IPv6 ekvivalentlari | `_is_public_ip()` |
| Javob hajmi (256 KB), vaqti (6 s) va redirect soni (5) cheklangan | `apps/core/net.py` |
| HSTS 1 yil + preload + subdomenlar | `production.py` |
| CSP: `script-src 'self'`, `frame-ancestors 'none'`, `object-src 'none'` | backend + `vercel.json` |
| Media fayllarga alohida tor CSP (`sandbox`) va `nosniff` | `config/wsgi.py` |
| `Permissions-Policy`, `Cross-Origin-Resource-Policy`, `Server` sarlavhasi o'chirilgan | `apps/core/middleware.py` |
| Cookie'lar: `Secure`, `HttpOnly`, `SameSite=Lax` | `production.py` |

### DoS va suiiste'mol

| Himoya | Qayerda |
|---|---|
| Har bir manzil turiga alohida limit (`anon`, `lead`, `auth`, `result`, `revision`, `health`) | `DEFAULT_THROTTLE_RATES` |
| Formalarda honeypot maydoni | `LeadForm.vue`, serializerlar |
| **Xabar yuborish so'rov oqimida emas** — sekin SMTP saytni to'xtata olmaydi | `apps/leads/services.py` |
| Fon oqimlari soni cheklangan (8 ta) | `_MAX_WORKERS` |
| Kesh kaliti faqat oq ro'yxatdagi parametrlardan — keshni to'ldirib bo'lmaydi | `apps/core/cache.py` |
| Bosh sahifa javobidagi har bir bo'lim cheklangan (24 ta) | `HOME_SECTION_LIMIT` |

### Konfiguratsiya

Production noto'g'ri sozlangan bo'lsa jarayon **umuman ishga tushmaydi**
(`ImproperlyConfigured`): bo'sh `ALLOWED_HOSTS`, bo'sh `CORS_ALLOWED_ORIGINS`,
standart `SECRET_KEY`, bir-birining ichidagi media papkalari, noto'g'ri
`ADMIN_ALLOWED_IPS`.

Testlar hech qachon masofaviy bazaga ulanmaydi (`config/settings/test.py`),
lokal muhit esa production Atlas'ga tasodifan yozib qo'ymaydi (`local.py`).

---

## Avtomatik tekshiruvlar

Har bir push va pull request'da (`.github/workflows/ci.yml`):

```
ruff check .                       # S (bandit) qoidalari bilan
python manage.py check             # sozlamalar
pytest -q                          # 72 ta test, shundan 42 tasi — xavfsizlik
python manage.py check --deploy --fail-level WARNING
pip-audit --strict                 # Python paketlaridagi ma'lum zaifliklar
npm audit --omit=dev --audit-level=high
eslint . --max-warnings 0
```

`tests/test_security.py` — har bir tuzatilgan zaiflik uchun alohida
regressiya testi. Zaiflik qaytib kelsa, test darhol qizil bo'ladi.

## Sirlar

Repozitoriyda hech qanday sir yo'q. `.env` `.gitignore` da; kerakli
o'zgaruvchilar ro'yxati `backend/.env.example` da (u yerda faqat bo'sh
qiymatlar va izohlar).

Sir sizib chiqqan deb gumon qilsangiz: `DJANGO_SECRET_KEY` ni almashtiring
(barcha JWT va sessiyalar darhol yaroqsiz bo'ladi), MongoDB parolini
yangilang, `ADMIN_URL` ni o'zgartiring.
