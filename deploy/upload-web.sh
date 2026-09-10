#!/bin/bash
#
# Yig'ilgan frontend'ni STDIN dan (tar.gz) qabul qiladi va joyiga qo'yadi.
#
# Almashtirish ATOMAR: yangi versiya avval yonidagi papkaga ochiladi, so'ng
# `mv` bilan almashtiriladi. Aks holda nusxalash paytida saytga kirgan odam
# yarim yangilangan katalogni ko'rardi (yangi HTML, eski assets — bo'sh sahifa).
set -euo pipefail

ROOT="/home/mars/mars-it-school"
LIVE="$ROOT/web/school"
NEW="$ROOT/web/.school-new"
OLD="$ROOT/web/.school-old"
LOG="$ROOT/logs/deploy.log"

rm -rf "$NEW" "$OLD"
mkdir -p "$NEW"

# `tar` STDIN dan o'qiydi; hajm cheklovi — cheksiz oqim diskni to'ldirmasin.
head -c 100M | tar -xzf - -C "$NEW"

if [ ! -f "$NEW/index.html" ]; then
    echo "XATO: arxivda index.html yo'q — almashtirilmadi." >&2
    rm -rf "$NEW"
    exit 1
fi

chmod -R a+rX "$NEW"
if [ -d "$LIVE" ]; then mv "$LIVE" "$OLD"; fi
mv "$NEW" "$LIVE"
rm -rf "$OLD"

printf '[%s] frontend yangilandi: %s fayl, %s\n' \
    "$(date -Is)" "$(find "$LIVE" -type f | wc -l)" "$(du -sh "$LIVE" | cut -f1)" >> "$LOG"
echo "frontend OK: $(find "$LIVE" -type f | wc -l) fayl"
