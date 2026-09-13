# Mars IT School — сайт школы

Маркетинговый сайт Mars IT School. Написан интернами на Django, переписан на
FastAPI и доведён до продакшена на mars.

- **LIVE:** https://core.marsit.uz/school/
- **Upstream:** `Ismoil-21/Mars-IT-School` · **наш форк:** `KogaCyber/Mars-IT-School`
- **Архитектура:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — читать первым

## Стек

| Часть | Что |
|---|---|
| `api/` | **FastAPI** + SQLAlchemy 2 (async) + asyncpg + Alembic, Python 3.10 (потолок на mars) |
| `frontend/` | Vue 3 + Vite + Tailwind, SPA + пререндер на 3 языка (uz/ru/en) |
| БД сайта | PostgreSQL 17 `mars_it_school` на `127.0.0.1:5437`, роль `school` |
| БД LMS | `gamification_db` на `:5432` — **только чтение**, роль `school_ro`, 4 таблицы |

**Принцип: читаем из LMS, пишем к себе.** Преподаватели, программы, филиалы,
вакансии — из базы геймификации, без копий. Маркетинговые надстройки (тексты,
картинки, цены) — свои таблицы со ссылкой `*_id`. Сайт **физически не может**
писать в LMS: у роли только `SELECT`.

Три языка живут как три поля (`title_ru/uz/en`), пустой перевод падает на `ru`.

## Прод на mars

```
/home/mars/mars-it-school/
├── api/               FastAPI, venv python3.10, .env (chmod 600 — единственный конфиг)
├── web/school/        собранный фронт (сюда кладёт CI)
├── data/media/        загруженные картинки — отдаёт nginx
├── data/private-media/резюме кандидатов, chmod 700 — по HTTP не отдаются вообще
├── deploy/            скрипты деплоя и копия nginx-конфига
└── logs/              api.err.log — смотреть первым
```

| Что | Где |
|---|---|
| backend | supervisor `school_api` → uvicorn `127.0.0.1:3530`, 2 воркера |
| маршрутизация | Caddy :443 → nginx :8880 (vhost `core.marsit.uz`, блок `/school/`) → uvicorn |
| бэкап БД | cron 23:20, `/home/mars/backups/backup_mars_it_school.sh`, выгрузка в Telegram |

Сайт живёт **под-путём**. Три вещи, которые легко сломать:

1. `ROOT_PATH=/school` в `.env` — nginx **срезает** префикс (`proxy_pass` со
   слэшем), FastAPI добавляет его в URL картинок. Уберёшь одно из двух — битые ссылки.
2. `VITE_BASE_PATH=/school/` на фронте — иначе ассеты и языки уедут в корень домена.
3. **`NUM_PROXIES=2`** — Caddy и nginx дают два хопа в `X-Forwarded-For`. При `1`
   клиентом считается `127.0.0.1` и лимит заявок бьёт по всем сразу.

## Деплой

Push в `prod` → GitHub Actions. Подробности в [deploy/README.md](deploy/README.md).

## Локально

```bash
cd api && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
# Postgres на localhost:5432, роль/база mars_it_school (см. tests/conftest.py)
.venv/bin/alembic upgrade head && .venv/bin/python manage.py sync-sections
.venv/bin/uvicorn app.main:app --port 8000 --reload
cd ../frontend && npm ci && npm run dev        # прокси /api → :8000
```

Тесты: `cd api && .venv/bin/pytest -q` — отдельная база `mars_it_school_test`,
LMS выключен, в геймификацию тесты не ходят никогда.

## Чего нет

- **Админки.** Контент правится визуальным редактором (этап 2, в работе) —
  открыть страницу, включить правку, кликнуть по тексту. Пока его нет —
  только SQL/скрипты.
- **Контента** — курсы/новости/филиалы на сайте пустые; LMS-данные подтянутся
  как только появятся записи-надстройки.
- **Уведомлений о заявках** — `LEAD_NOTIFY_EMAILS`, `TELEGRAM_*` в `.env` пустые.
- **Шрифтов Actay** — лицензионные, в репозитории их никогда не было.

## Грабли

- **Django-версия жила до 2026-09-14** (Mongo → Postgres → FastAPI за неделю).
  В истории гита и в `DEPLOY.md`/`SECURITY.md` интернов упоминания Django,
  Railway, Mongo — прошлое.
- `id` в API — целое число. `price` — строка (`"800000"`), так ждёт фронт.
- Секции страниц (49 блоков) описаны в `api/app/content/sections.json`,
  стандартные тексты — `section_defaults.json`. `sync-sections` создаёт
  недостающие и **не трогает** уже отредактированные.
- Кэш публичных GET — 60 с, ключ включает версию контента: после правки
  ответ обновляется сразу (`services/revision.py`).
