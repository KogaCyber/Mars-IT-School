# Деплой на mars

Push в `prod` → GitHub Actions `.github/workflows/deploy.yml`. Ничего руками.

```
push в prod
  → CI (backend py3.10 + py3.12, frontend lint/test/build)   ← красный = деплоя нет
  → сборка фронта на раннере
  → ssh upload   тарболл фронта → web/school/ (атомарная подмена)
  → ssh deploy   git reset --hard origin/prod, migrate, collectstatic, restart
  → ssh status   supervisor + /health/ + /api/v1/home/
  → curl снаружи https://core.marsit.uz/school/…
```

Фронт собирается **на раннере**, а не на сервере: на mars стоит Node 12, и
машина и так загружена.

## Ключ деплоя ограничен

У пользователя `mars` в sudoers прописано `(ALL) NOPASSWD: ALL` — то есть
беспарольный root. Обычный SSH-ключ в GitHub Secrets означал бы root на
проде геймификации: репозиторий публичный, а к секретам имеет доступ любой,
кто может запустить workflow.

Поэтому в `~/.ssh/authorized_keys` ключ прибит forced command'ом:

```
command="/home/mars/mars-it-school/deploy/ssh-gate.sh",no-agent-forwarding,no-port-forwarding,no-pty,no-user-rc,no-X11-forwarding ssh-ed25519 AAAA...
```

`ssh-gate.sh` смотрит на `SSH_ORIGINAL_COMMAND` и понимает ровно три слова —
`upload`, `deploy`, `status`. Аргументы не принимаются, так что дописать
что-то к команде нельзя. Шелл, `sudo`, произвольные команды — отказ и запись
в `logs/deploy.log`.

Проверить, что ограничение живо:

```bash
ssh -i deploy_key mars@marsit.uz status   # работает
ssh -i deploy_key mars@marsit.uz id       # отказ, exit 1
ssh -i deploy_key mars@marsit.uz          # отказ, интерактива нет
```

`deploy.sh` дополнительно жёстко зашивает ветку `prod` — ключом нельзя
выкатить произвольный коммит.

## Секреты репозитория

| Секрет | Что |
|---|---|
| `MARS_SSH_KEY` | приватный ключ деплоя (ed25519) |
| `MARS_HOST` | `marsit.uz` |
| `MARS_USER` | `mars` |
| `MARS_KNOWN_HOSTS` | вывод `ssh-keyscan marsit.uz` |

`known_hosts` заполнен намеренно: с `StrictHostKeyChecking=no` человек
посередине принял бы деплой на себя.

## Ротация ключа

```bash
ssh-keygen -t ed25519 -f deploy_key -N "" -C "github-actions-deploy@mars-it-school"
# на сервере: заменить строку с этим комментарием в ~/.ssh/authorized_keys,
# СОХРАНИВ префикс command="..." — без него ключ станет полноценным root'ом
gh secret set MARS_SSH_KEY --repo KogaCyber/Mars-IT-School < deploy_key
```

## Если CI недоступен

```bash
ssh mars@marsit.uz
cd /home/mars/mars-it-school && ./deploy/deploy.sh && ./deploy/status.sh
```

Фронт при этом не обновится — он собирается на раннере. Локально:
`cd frontend && npm run build && tar -czf - -C dist . | ssh -i deploy_key mars@marsit.uz upload`

## nginx

Vhost `core.marsit.uz` **общий с фронтом геймификации** и деплоем не трогается —
CI кладёт только файлы в `web/school/`. Копия конфига для справки:
[`deploy/nginx/core.marsit.uz.conf`](nginx/core.marsit.uz.conf).

Правки — руками и только вне окна занятий:

```bash
sudo cp /etc/nginx/sites-enabled/core.marsit.uz /home/mars/nginx-backups/core.marsit.uz.$(date +%Y%m%d-%H%M%S)
# правим, затем:
sudo nginx -t && sudo nginx -s reload
```

Бэкапы держать в `/home/mars/nginx-backups/`, **не** рядом с активным конфигом:
nginx читает `sites-enabled/*` целиком, и `.bak` даёт дубль `server_name`.

Две неочевидные вещи в конфиге:

- `proxy_pass` для `/school/api/`, админки и `/school/i18n/` — **со слэшем на
  конце**. Он срезает префикс, а Django возвращает его через `FORCE_SCRIPT_NAME`.
  Уберёшь слэш — Django получит `/school/api/...` и отдаст 404 на всё.
- Запросы с расширением файла (`.woff2`, `.css`, `.png` …) отдают честный **404**,
  а не `index.html`. Иначе браузер получает HTML вместо шрифта и пишет
  `invalid sfntVersion: 1008821359` — это число и есть `<!DO`.

## Окно деплоя

mars — прод геймификации. Не деплоить **10:00–12:30** и **14:00–18:00** UZT:
в эти часы идут занятия. Сам по себе `school_api` геймификацию не трогает, но
правка nginx или что-то, что тянет за собой reload, — трогает.
