#!/bin/bash
#
# Backend deploy: kodni yangilaydi, migratsiya va statikani bajaradi, xizmatni
# qayta ishga tushiradi. GitHub Actions `ssh ... deploy` orqali chaqiradi
# (`ssh-gate.sh` ga qarang) — argument qabul qilmaydi, ya'ni bu skript
# BAJARADIGAN ishlar ro'yxati serverda, repozitoriyda emas.
#
# `prod` shoxidan boshqa hech narsa yig'ilmaydi: deploy kaliti tasodifiy
# (yoki yomon niyatli) shoxni productionga chiqara olmasligi kerak.
set -euo pipefail

ROOT="/home/mars/mars-it-school"
BACKEND="$ROOT/backend"
BRANCH="prod"
LOG="$ROOT/logs/deploy.log"
mkdir -p "$ROOT/logs"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$LOG"; }

# Butun skript FUNKSIYA ichida va oxirida chaqiriladi. Sabab: `git reset`
# shu faylning O'ZINI ham yangilaydi, bash esa skriptni bajarayotib qatorma-qator
# o'qiydi — o'zgargan fayldan keyingi qator tasodifiy joydan o'qilishi mumkin.
# Funksiya butunlay o'qilib bo'lgach bajariladi, keyingi o'zgarish unga tegmaydi.
main() {
    cd "$ROOT"
    before=$(git rev-parse --short HEAD)

    log "fetch origin/$BRANCH"
    git fetch --quiet origin "$BRANCH"
    git reset --quiet --hard "origin/$BRANCH"
    after=$(git rev-parse --short HEAD)
    log "kod: $before -> $after ($(git log -1 --pretty=%s))"

    cd "$BACKEND"
    export DJANGO_SETTINGS_MODULE=config.settings.production

    # Paketlar faqat requirements.txt o'zgarganda o'rnatiladi: har deploy'da
    # `pip install` yurgizish yuklangan serverda bir necha daqiqa oladi.
    # `:/` — yo'l repozitoriy ILDIZIdan: bu yerda CWD allaqachon backend/, va oddiy
    # `backend/requirements.txt` CWD'ga nisbatan `backend/backend/...` bo'lib,
    # hech qachon topilmasdi — diff bo'sh, "o'zgarmadi", paket o'rnatilmasdi.
    # Postgres'ga o'tishda aynan shu sabab psycopg o'rnatilmay deploy yiqildi.
    if ! git diff --quiet "$before" "$after" -- ":/backend/requirements.txt" 2>/dev/null; then
        log "requirements.txt o'zgardi — paketlar yangilanmoqda"
        .venv/bin/pip install --quiet -r requirements.txt
    else
        log "requirements.txt o'zgarmadi — paketlar o'tkazib yuborildi"
    fi

    log "migrate"
    .venv/bin/python manage.py migrate --noinput 2>&1 | tail -5 | tee -a "$LOG"

    log "sync_sections"
    .venv/bin/python manage.py sync_sections 2>&1 | tail -2 | tee -a "$LOG"

    log "collectstatic"
    .venv/bin/python manage.py collectstatic --noinput 2>&1 | tail -2 | tee -a "$LOG"

    log "restart school_api"
    sudo -n /usr/bin/supervisorctl restart school_api 2>&1 | tee -a "$LOG"

    # Gunicorn `--preload` bilan ishlaydi: worker'lar ko'tarilishiga vaqt kerak.
    sleep 8
    log "deploy tugadi ($after)"
}

main "$@"
