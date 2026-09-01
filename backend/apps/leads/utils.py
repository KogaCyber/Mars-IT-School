"""Arizalar bilan ishlashda kerak bo'ladigan yordamchilar."""

from django.conf import settings


def client_ip(request) -> str | None:
    """Proksi (Railway) orqasidagi haqiqiy IP manzilni aniqlaydi.

    `X-Forwarded-For` — mijoz o'zi ham yubora oladigan sarlavha, shuning uchun
    uning boshidagi qiymatga ishonib bo'lmaydi (soxtalashtirilishi mumkin).
    Zanjirning oxiridan `NUM_PROXIES` ta qadam orqaga qaytilganda bizning
    ishonchli proksimiz yozgan manzil olinadi.
    """
    proxies = getattr(settings, "NUM_PROXIES", 0)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")

    if proxies and forwarded:
        addresses = [part.strip() for part in forwarded.split(",") if part.strip()]
        if addresses:
            return addresses[-min(proxies, len(addresses))][:45] or None

    return request.META.get("REMOTE_ADDR")
