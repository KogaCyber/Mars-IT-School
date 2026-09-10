#!/bin/bash
# Deploy'dan keyingi tekshiruv. Xizmat ko'tarilmasa — nol bo'lmagan kod,
# ya'ni CI qizil bo'ladi va buzilgan deploy sezilmay qolmaydi.
set -uo pipefail

PORT=3530
HOST_HEADER="core.marsit.uz"
fail=0

state=$(sudo -n /usr/bin/supervisorctl status school_api 2>/dev/null | awk '{print $2}')
echo "supervisor: ${state:-NOMA'LUM}"
[ "$state" = "RUNNING" ] || fail=1

health=$(curl -s --max-time 10 -H "Host: $HOST_HEADER" -H "X-Forwarded-Proto: https" \
    "http://127.0.0.1:$PORT/health/" 2>/dev/null)
echo "health: ${health:-<javob yo'q>}"
echo "$health" | grep -q '"database":true' || fail=1

code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -H "Host: $HOST_HEADER" \
    -H "X-Forwarded-Proto: https" "http://127.0.0.1:$PORT/api/v1/home/" 2>/dev/null)
echo "api/v1/home: $code"
[ "$code" = "200" ] || fail=1

# Deploy'dan keyin paydo bo'lgan traceback — jimgina buzilgan reliz belgisi.
if [ -f /home/mars/mars-it-school/logs/error.log ]; then
    recent=$(find /home/mars/mars-it-school/logs/error.log -newermt '-3 minutes' 2>/dev/null)
    if [ -n "$recent" ] && grep -q "Traceback" /home/mars/mars-it-school/logs/error.log; then
        echo "DIQQAT: loglarda yangi traceback bor"
        tail -20 /home/mars/mars-it-school/logs/error.log
    fi
fi

[ "$fail" = 0 ] && echo "TEKSHIRUV: OK" || echo "TEKSHIRUV: MUAMMO BOR"
exit "$fail"
