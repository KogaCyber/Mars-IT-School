"""Xavfsizlik middleware'lari.

Django'ning `SecurityMiddleware` bir nechta muhim sarlavhani qo'yadi
(HSTS, nosniff, referrer policy), lekin hammasini emas. Bu yerda qolganlari
qo'shiladi va admin panel uchun qo'shimcha qavat yopiladi.
"""

import ipaddress
import logging

from django.conf import settings
from django.http import HttpResponseNotFound

security_log = logging.getLogger("security.audit")


class SecurityHeadersMiddleware:
    """Django qo'ymaydigan zamonaviy himoya sarlavhalarini qo'shadi.

    * **Permissions-Policy** — API domenida kamera, mikrofon, geolokatsiya,
      to'lov kabi brauzer imkoniyatlari umuman kerak emas. Ular yopilsa,
      XSS yuz bergan taqdirda ham hujumchi bu qurilmalarni so'ray olmaydi.
    * **Cross-Origin-Resource-Policy** — backend javoblarini boshqa saytlar
      o'z sahifasiga resurs sifatida tortib olishining oldini oladi
      (Spectre uslubidagi yon kanal hujumlariga qarshi qavat).
    * **Cross-Origin-Embedder-Policy** — shu himoyaning ikkinchi yarmi.
    * **`Server` sarlavhasi** — gunicorn o'z nomi va versiyasini e'lon qiladi.
      Bu hujumchiga tayyor ma'lumot: qaysi versiyada qanday zaiflik borligini
      qidirish uchun. Uni olib tashlaymiz.

    Diqqat: CORP `same-origin` emas, `cross-origin` — sayt boshqa domenda
    (Vercel) va rasmlarni backenddan yuklaydi. `same-origin` qo'yilsa
    saytdagi barcha rasmlar bloklanardi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response.setdefault(
            "Permissions-Policy",
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=(), "
            "interest-cohort=()",
        )
        response.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")

        # `del` yo'q sarlavhada xatolik bermaydi (Django `HttpResponse` da).
        if response.has_header("Server"):
            del response["Server"]

        return response


class AdminAccessMiddleware:
    """Admin panelga kirishni IP bo'yicha cheklaydi va urinishlarni qayd etadi.

    Admin panel — saytdagi eng qimmatli nishon: u yerdan barcha kontent,
    arizalar va nomzodlarning rezyumesi ko'rinadi. Uni himoya qiladigan
    yagona narsa parol bo'lib qolmasligi kerak.

    Qavatlar:

    1. **`ADMIN_ALLOWED_IPS`** — bo'sh bo'lsa cheklov yo'q (standart holat,
       chunki ko'p jamoada statik IP bo'lmaydi). To'ldirilsa — faqat shu
       manzillar (yoki tarmoqlar, masalan `84.54.72.0/24`) kira oladi.
       Qolganlar 404 oladi, 403 emas: 403 «bu yerda admin panel bor» degan
       tasdiq bo'lardi.
    2. **Qayd (audit)** — ruxsatsiz urinish loggerga yoziladi. Maxfiy
       `ADMIN_URL` ga begona IP dan so'rov kelishi — manzil sizib chiqqanining
       birinchi belgisi.

    Middleware `SERVICE_HAS_ADMIN` bo'lmasa umuman ishlamaydi.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Sayt yo'l prefiksida turishi mumkin (`FORCE_SCRIPT_NAME`, masalan
        # `/school`). `request.path` prefiksni ham o'z ichiga oladi, shuning
        # uchun taqqoslanadigan namuna ham prefiks bilan qurilishi kerak —
        # aks holda bu middleware admin so'rovini umuman tanimay, IP cheklovi
        # va qayd (audit) jimgina o'chib qolardi.
        script_name = (getattr(settings, "FORCE_SCRIPT_NAME", "") or "").rstrip("/")
        self.prefix = f"{script_name}/{settings.ADMIN_URL.lstrip('/')}"
        self.networks = self._parse(getattr(settings, "ADMIN_ALLOWED_IPS", []))

    @staticmethod
    def _parse(values) -> list:
        """Matn ro'yxatini tarmoqlar ro'yxatiga aylantiradi.

        Bitta IP (`84.54.72.10`) ham, tarmoq (`84.54.72.0/24`) ham qabul
        qilinadi. Noto'g'ri yozilgani jimgina tashlab yuborilmaydi —
        `ImproperlyConfigured` sozlamalarda ko'tariladi, bu yerda esa
        shunchaki e'tiborga olinmaydi.
        """
        networks = []
        for value in values:
            try:
                networks.append(ipaddress.ip_network(str(value).strip(), strict=False))
            except ValueError:
                security_log.error("ADMIN_ALLOWED_IPS: noto'g'ri qiymat %r", value)
        return networks

    def _allowed(self, ip: str | None) -> bool:
        if not self.networks:
            return True
        if not ip:
            return False
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return any(address in network for network in self.networks)

    def __call__(self, request):
        if not settings.SERVICE_HAS_ADMIN or not request.path.startswith(self.prefix):
            return self.get_response(request)

        # Import shu yerda: `apps.leads` ilovasi yuklanishini kutmaymiz.
        from apps.leads.utils import client_ip

        ip = client_ip(request)
        if not self._allowed(ip):
            security_log.warning(
                "Admin panelga ruxsatsiz IP dan urinish: ip=%s path=%s ua=%s",
                ip,
                request.path,
                request.META.get("HTTP_USER_AGENT", "")[:200],
            )
            # 404 — manzilning mavjudligini tasdiqlamaslik uchun.
            return HttpResponseNotFound("Not found")

        return self.get_response(request)
