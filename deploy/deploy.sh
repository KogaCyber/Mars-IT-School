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
API="$ROOT/api"
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

    cd "$API"

    # Paketlar faqat requirements.txt o'zgarganda o'rnatiladi: har deploy'da
    # `pip install` yurgizish yuklangan serverda bir necha daqiqa oladi.
    # `:/` — yo'l repozitoriy ILDIZIdan (CWD bu yerda api/).
    if ! git diff --quiet "$before" "$after" -- ":/api/requirements.txt" 2>/dev/null; then
        log "requirements.txt o'zgardi — paketlar yangilanmoqda"
        .venv/bin/pip install --quiet -r requirements.txt
    else
        log "requirements.txt o'zgarmadi — paketlar o'tkazib yuborildi"
    fi

    log "alembic upgrade head"
    .venv/bin/alembic upgrade head 2>&1 | tail -3 | tee -a "$LOG"

    log "sync-sections"
    .venv/bin/python manage.py sync-sections 2>&1 | tail -2 | tee -a "$LOG"

    log "restart school_api"
    sudo -n /usr/bin/supervisorctl restart school_api 2>&1 | tee -a "$LOG"

    # Uvicorn worker'lari va baza ulanishlari ko'tarilishiga vaqt kerak.
    sleep 6
    log "deploy tugadi ($after)"
}

main "$@"
