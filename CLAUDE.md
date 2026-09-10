# Mars IT School — сайт школы

Маркетинговый сайт Mars IT School. Написан интернами, форкнут и доведён до
продакшена на mars.

- **LIVE:** https://core.marsit.uz/school/
- **Админка:** `https://core.marsit.uz/school/<секретный-путь>/` — путь в
  `backend/.env` на сервере (`ADMIN_URL`), в гит не попадает
- **Upstream:** `Ismoil-21/Mars-IT-School` · **наш форк:** `KogaCyber/Mars-IT-School`

## Стек

| Часть | Что |
|---|---|
| backend | Django 5.2 + DRF, БД — **MongoDB** через `django-mongodb-backend` |
| frontend | Vue 3 + Vite + Tailwind, SPA + пререндер статики на 3 языка (uz/ru/en) |
| админка | Django admin, вся контентная модель редактируется там |

Три языка живут как три поля модели (`title_ru`/`title_uz`/`title_en`), а не как
отдельные записи. Пустой перевод падает обратно на `ru`.

## Прод на mars

```
/home/mars/mars-it-school/
├── backend/           Django, venv на python3.10 (3.11+ на mars нет)
│   ├── .env           секреты, chmod 600 — единственный источник конфига
│   └── staticfiles/   collectstatic, отдаётся nginx'ом напрямую
├── web/school/        собранный фронт (сюда кладёт CI)
├── data/media/        загруженные картинки
├── data/private-media/резюме кандидатов, chmod 700 — НЕ отдаётся статикой
├── deploy/            скрипты деплоя (см. deploy/README.md)
└── logs/
```

| Что | Где |
|---|---|
| backend | supervisor `school_api` → gunicorn `127.0.0.1:3530` |
| MongoDB | docker `mars-it-school-mongo` (mongo:7) на `127.0.0.1:27020` |
| маршрутизация | Caddy :443 → nginx :8880 → gunicorn |
| vhost | `/etc/nginx/sites-enabled/core.marsit.uz`, блок `/school/` |

Сайт живёт **под-путём** на чужом домене. Из этого следует три вещи, которые
легко сломать:

1. `FORCE_SCRIPT_NAME=/school` — nginx **срезает** префикс (`proxy_pass` со
   слэшем на конце), Django добавляет его обратно во все ссылки, которые
   генерирует сам. Уберёшь одно из двух — админка отдаст 404 на каждую ссылку.
2. `VITE_BASE_PATH=/school/` на фронте — иначе ассеты, определение языка и
   ссылки в пререндеренном HTML уедут в корень домена.
3. **`NUM_PROXIES=2`** — Caddy и nginx дают два хопа в `X-Forwarded-For`.
   При `1` Django видит клиентом `127.0.0.1`, и один неверный пароль в
   django-axes банит вообще всех.

## Деплой

Push в `prod` → GitHub Actions. Подробности в [deploy/README.md](deploy/README.md).
Руками ничего делать не нужно.

## Чего в проекте нет

- **Контента.** База заводится пустой; курсы, новости, преподаватели и филиалы
  вносятся через админку либо восстанавливаются из дампа интернов.
- **Почты и Telegram-уведомлений о заявках** — `LEAD_NOTIFY_EMAILS`,
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` в `.env` пустые. Заявки копятся в
  админке, но никому не приходят.

## Грабли

- **MongoDB нужна ≥ 6.0.** Системная монга на mars — 5.0, она для другого;
  у проекта свой контейнер на 27020. Не переключать на 27017.
- **Python 3.10 — потолок на mars.** `datetime.UTC` и прочее из 3.11+ упадёт на
  импорте. CI гоняет матрицу 3.10 + 3.12 именно поэтому.
- **`config/settings/base.py` требует `DJANGO_SECRET_KEY` в момент импорта.**
  Переопределять его *после* `from .base import *` бесполезно — так у интернов
  и лежал сломанный `test.py`, из-за чего CI не проходил ни разу.
- **Резюме кандидатов — персональные данные.** Лежат вне `MEDIA_ROOT`, отдаются
  только через `resume_download_view` с правами сотрудника. `PRIVATE_MEDIA_ROOT`
  внутри `MEDIA_ROOT` класть нельзя — приложение специально не стартует.
- **Тесты гоняются только в корневом режиме.** Под `FORCE_SCRIPT_NAME` тестовый
  клиент Django не подставляет префикс и половина тестов краснеет — это
  особенность клиента, не баг.
