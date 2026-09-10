#!/bin/bash
#
# Deploy kaliti uchun DARVOZA (authorized_keys ichidagi `command="..."`).
#
# Nega kerak: `mars` foydalanuvchisida sudoers'da `(ALL) NOPASSWD: ALL` turibdi,
# ya'ni bu hisobga kirgan har kim parolsiz root bo'ladi. Cheklovsiz deploy
# kaliti GitHub sirlariga solinsa, repozitoriyga (u OCHIQ fork) yoki
# Actions'ga kirish — bevosita gamification production serverida root degani.
#
# Shuning uchun kalit qobiq (shell) bermaydi: u faqat quyidagi uchta
# harakatni bajara oladi va hech qanday argument qabul qilmaydi — ya'ni
# `SSH_ORIGINAL_COMMAND` orqali hech narsani "qo'shib yuborish" mumkin emas.
set -euo pipefail

ROOT="/home/mars/mars-it-school"
LOG="$ROOT/logs/deploy.log"
mkdir -p "$ROOT/logs"

deny() {
    printf 'Bu kalit faqat deploy uchun. Ruxsat etilgan: upload | deploy | status\n' >&2
    printf '[%s] RAD ETILDI: %q (from %s)\n' \
        "$(date -Is)" "${SSH_ORIGINAL_COMMAND:-(bosh)}" "${SSH_CONNECTION%% *}" >> "$LOG"
    exit 1
}

case "${SSH_ORIGINAL_COMMAND:-}" in
    upload) exec "$ROOT/deploy/upload-web.sh" ;;
    deploy) exec "$ROOT/deploy/deploy.sh" ;;
    status) exec "$ROOT/deploy/status.sh" ;;
    *)      deny ;;
esac
