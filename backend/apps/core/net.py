"""Tashqi manzillarga SSRF'dan himoyalangan murojaat.

Nega alohida modul kerak: serverning o'zi so'rov yuboradigan har bir joy
(xarita havolasini ochish, geokodlash) hujumchi uchun «ichkariga teshik»
bo'lishi mumkin. Klassik SSRF stsenariysi:

    admin  →  https://goo.gl/xyz  →  (redirect)  →  http://169.254.169.254/…

Manzil tekshiruvi FAQAT boshlang'ich havolaga qo'llansa, redirect'dan keyingi
manzil hech kim tomonidan ko'rilmaydi va server bulut provayderining
metadata xizmatiga yoki ichki tarmoqdagi (Railway private network) xizmatga
so'rov yuboradi.

Shuning uchun bu modulda uch qavatli himoya:

1. **Domen oq ro'yxati** — faqat oldindan ma'lum xostlar.
2. **IP tekshiruvi** — domen DNS orqali qaysi IP'ga ishora qilishi tekshiriladi.
   Bu «DNS rebinding» va oq ro'yxatdagi domenni ichki IP'ga yo'naltirishga
   qarshi (`nip.io` uslubidagi hiylalar).
3. **Har bir redirect qadamida 1 va 2 QAYTA bajariladi** — zanjirning oxirgi
   halqasi ham xuddi birinchisi kabi tekshiriladi.

Bundan tashqari javob hajmi va vaqti cheklanadi: cheksiz oqim yuboradigan
server worker'ni abadiy band qilib qo'ymasligi kerak.
"""

import ipaddress
import logging
import socket
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

#: So'rov shuncha soniyadan ko'p davom etmaydi.
DEFAULT_TIMEOUT = 6

#: Javobdan shuncha baytdan ko'pi o'qilmaydi (~256 KB).
MAX_RESPONSE_BYTES = 256 * 1024

#: Redirect zanjiri shuncha qadamdan uzun bo'lmaydi.
MAX_REDIRECTS = 5


class UnsafeUrlError(ValueError):
    """Manzil oq ro'yxatdan tashqarida yoki ichki tarmoqqa ishora qiladi."""


def _is_public_ip(raw: str) -> bool:
    """IP ommaviy internetga tegishlimi.

    Rad etiladi: loopback (127.0.0.0/8), xususiy tarmoqlar (10/8, 172.16/12,
    192.168/16), link-local (169.254/16 — AWS/GCP metadata aynan shu yerda),
    CGNAT (100.64/10), multicast, reserved va IPv6 dagi ekvivalentlari
    (::1, fc00::/7, fe80::/10), shu jumladan IPv4-mapped IPv6 (::ffff:127.0.0.1).
    """
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        return False

    # `::ffff:10.0.0.1` ko'rinishidagi manzil IPv6 sifatida "global" ko'rinishi
    # mumkin — shuning uchun avval IPv4 ekvivalentiga keltiriladi.
    if getattr(address, "ipv4_mapped", None):
        address = address.ipv4_mapped

    if not address.is_global:
        return False
    # `is_global` CGNAT (100.64.0.0/10) ni ba'zi versiyalarda o'tkazib yuboradi.
    return address not in ipaddress.ip_network("100.64.0.0/10")


def _resolve_is_public(host: str) -> bool:
    """Domen ishora qiladigan BARCHA IP manzillar ommaviymi.

    Bittasi ham ichki bo'lsa — rad etamiz. Domen bir nechta yozuvga ega
    bo'lishi mumkin va hujumchi ulardan birini ichki manzil qilib qo'yishi
    mumkin edi.
    """
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError, ValueError):
        return False

    addresses = {info[4][0] for info in infos}
    return bool(addresses) and all(_is_public_ip(item) for item in addresses)


def host_of(url: str) -> str:
    """Manzilning `www.` siz xost qismi (kichik harflarda)."""
    return (urllib.parse.urlparse(url).hostname or "").lower().removeprefix("www.")


def is_allowed_host(url: str, allowed_hosts: tuple[str, ...]) -> bool:
    """Manzilning sxemasi, porti va domeni maqbulmi (TARMOQQA CHIQMAYDI).

    Bu «arzon» tekshiruv: uni manzilni shunchaki tahlil qilishda (masalan
    havoladan koordinata ajratib olishda) ishlatish mumkin — DNS ishlamayotgan
    bo'lsa ham natija bir xil bo'ladi.

    `host.endswith(f".{domain}")` — nuqta bilan: `google.com.evil.tld` yoki
    `evilgoogle.com` o'tib ketmasligi uchun.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    host = host_of(url)
    if not host:
        return False

    # Standart bo'lmagan port — ko'pincha ichki xizmat belgisi (redis, admin panel).
    try:
        port = parsed.port
    except ValueError:
        return False
    if port not in (None, 80, 443):
        return False

    return any(host == domain or host.endswith(f".{domain}") for domain in allowed_hosts)


def is_allowed_url(url: str, allowed_hosts: tuple[str, ...]) -> bool:
    """`is_allowed_host()` + domen ommaviy IP'ga ishora qilishini tekshirish.

    Bu tekshiruv TARMOQQA chiqadi (DNS), shuning uchun u faqat haqiqiy so'rov
    yuborishdan oldin qo'llaniladi.

    Halol eslatma: DNS javobi bilan ulanish o'rtasida nazariy «DNS rebinding»
    oynasi qoladi (nom qayta hal qilinadi). To'liq yopish uchun aniq IP'ga
    ulanib, `Host` sarlavhasini qo'lda qo'yish kerak bo'lardi. Bu yerda esa
    domenlar oq ro'yxati qisqa va ular boshqalarga tegishli (google, yandex,
    openstreetmap) — hujumchi ularning DNS yozuvini boshqara olmaydi, ya'ni
    rebinding amalda mumkin emas.
    """
    return is_allowed_host(url, allowed_hosts) and _resolve_is_public(host_of(url))


class _StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Har bir redirect manzilini oq ro'yxat bo'yicha QAYTA tekshiradi.

    `urllib` standart holatda redirect'ni jimgina kuzatadi — aynan shu
    xatti-harakat SSRF'ni ochib beradi. `None` qaytarilsa zanjir uziladi.
    """

    #: Zanjir shuncha qadamdan uzun bo'lsa `urllib` o'zi to'xtatadi.
    max_repeats = MAX_REDIRECTS
    max_redirections = MAX_REDIRECTS

    def __init__(self, allowed_hosts: tuple[str, ...]):
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not is_allowed_url(newurl, self.allowed_hosts):
            logger.warning(
                "SSRF himoyasi: redirect rad etildi (%s → %s)", req.full_url, newurl
            )
            raise UnsafeUrlError(f"Redirect ruxsat etilmagan manzilga: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def safe_open(
    url: str,
    *,
    allowed_hosts: tuple[str, ...],
    user_agent: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> tuple[str, bytes] | None:
    """Manzilni xavfsiz ochadi.

    Qaytaradi: `(yakuniy_manzil, javob_bayti)` yoki tekshiruvdan o'tmasa /
    xatolik bo'lsa — `None`. Hech qachon istisno ko'tarmaydi: chaqiruvchi
    tomonlar uchun bu «best effort» amal va u asosiy ishni to'xtatmasligi kerak.
    """
    if not is_allowed_url(url, allowed_hosts):
        logger.info("SSRF himoyasi: manzil rad etildi (%s)", url)
        return None

    opener = urllib.request.build_opener(_StrictRedirectHandler(allowed_hosts))
    # Sxema `is_allowed_url()` da http/https bilan cheklangan (file:, gopher:
    # va boshqalar rad etiladi), xost oq ro'yxatda va ommaviy IP'ga ishora
    # qiladi — ya'ni S310 tekshiruvi talab qiladigan hamma narsa bajarilgan.
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})  # noqa: S310

    try:
        # Manzil yuqorida oq ro'yxat va IP bo'yicha tekshirilgan, redirect'lar
        # esa `_StrictRedirectHandler` orqali har qadamda qayta tekshiriladi.
        with opener.open(request, timeout=timeout) as response:  # noqa: S310
            final_url = response.geturl()
            # Yakuniy tekshiruv: handler chetlab o'tilgan holat qolmasin.
            if not is_allowed_url(final_url, allowed_hosts):
                return None
            body = response.read(MAX_RESPONSE_BYTES)
    except UnsafeUrlError:
        return None
    except (urllib.error.URLError, ValueError, TimeoutError, OSError):
        logger.info("Tashqi manzil ochilmadi: %s", url)
        return None

    return final_url, body
