"""Yuklanadigan fayllarni tekshirish va xavfsiz nom berish.

Ikki muammoni hal qiladi.

**1. Fayl nomiga ishonib bo'lmaydi.** Kengaytmani tekshirish (`.pdf` bilan
tugaydimi) — bu shunchaki satr tekshiruvi. Hujumchi ixtiyoriy baytlarni
`cv.pdf` deb nomlab yuborishi mumkin: HTML sahifa, SVG (ichida skript
bo'ladi), zip-bomba yoki polyglot fayl. Shuning uchun faylning DASTLABKI
baytlari (magic number) ham tekshiriladi.

**2. Fayl nomining o'zi — shaxsiy ma'lumot.** `Ivanov_Ivan_rezyume.pdf`
diskda ham, `Content-Disposition` sarlavhasida ham nomzodning ismini oshkor
qiladi. Shuning uchun saqlashda nom tasodifiy qiymatga almashtiriladi.
"""

import secrets
from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

#: Rezyume uchun ruxsat etilgan turlar: kengaytma → mumkin bo'lgan
#: boshlang'ich baytlar (magic number).
#:
#: * PDF  — `%PDF`
#: * DOCX — `PK\x03\x04` (bu OOXML — aslida zip arxiv)
#: * DOC  — `\xd0\xcf\x11\xe0` (eski OLE2 formati)
#: * RTF  — `{\rtf`
RESUME_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF",),
    ".docx": (b"PK\x03\x04",),
    ".doc": (b"\xd0\xcf\x11\xe0", b"{\\rtf"),
    ".rtf": (b"{\\rtf",),
}

#: Rasm turlari — avatar va admin paneldagi suratlar uchun.
IMAGE_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".webp": (b"RIFF",),
    ".gif": (b"GIF87a", b"GIF89a"),
}

#: Signaturani tekshirish uchun shuncha bayt o'qiladi.
_HEADER_BYTES = 16


def _read_header(file) -> bytes:
    """Faylning boshidan bir necha bayt o'qiydi va kursorni joyiga qaytaradi."""
    position = file.tell() if hasattr(file, "tell") else 0
    try:
        file.seek(0)
        header = file.read(_HEADER_BYTES)
    finally:
        file.seek(position)
    return header or b""


def validate_upload(file, *, signatures: dict[str, tuple[bytes, ...]], max_bytes: int):
    """Yuklangan faylni kengaytma, hajm VA mazmun bo'yicha tekshiradi.

    Uchalasi ham kerak:

    * kengaytma — saqlanadigan fayl nomi uchun;
    * hajm — disk to'lib qolishi va xotira sarfiga qarshi;
    * signatura — «`.pdf` deb nomlangan HTML» ni rad etish uchun.

    Xatolik `django.core.exceptions.ValidationError` sifatida ko'tariladi —
    uni DRF serializer ham, model `full_clean()` ham tushunadi.
    """
    if file is None:
        return file

    suffix = Path(file.name or "").suffix.lower()
    if suffix not in signatures:
        allowed = ", ".join(sorted(signatures))
        raise ValidationError(
            _("Fayl turi mos emas. Ruxsat etilgan: %(allowed)s."),
            code="invalid_extension",
            params={"allowed": allowed},
        )

    size = getattr(file, "size", 0) or 0
    if size > max_bytes:
        raise ValidationError(
            _("Fayl hajmi %(limit)s MB dan oshmasligi kerak."),
            code="too_large",
            params={"limit": max_bytes // (1024 * 1024)},
        )
    if size == 0:
        raise ValidationError(_("Fayl bo'sh."), code="empty")

    header = _read_header(file)
    if not any(header.startswith(magic) for magic in signatures[suffix]):
        # Ataylab umumiy xabar: qaysi signatura kutilayotgani hujumchiga
        # keraksiz ma'lumot beradi.
        raise ValidationError(
            _("Fayl mazmuni uning turiga mos kelmadi."), code="content_mismatch"
        )

    return file


def random_upload_name(instance, filename: str, *, prefix: str) -> str:
    """Faylga tasodifiy nom beradi: `<prefix>/<yil>/<oy>/<32 belgi><kengaytma>`.

    Nomzodning ismi na diskda, na `Content-Disposition` sarlavhasida
    ko'rinmaydi; nomni taxmin qilib faylni so'rab olish ham mumkin emas.
    """
    from django.utils import timezone

    suffix = Path(filename or "").suffix.lower()[:10]
    now = timezone.now()
    return f"{prefix}/{now:%Y/%m}/{secrets.token_hex(16)}{suffix}"


def resume_upload_to(instance, filename: str) -> str:
    """`VacancyApplication.resume` uchun yo'l (migratsiyada nomi bilan yoziladi)."""
    return random_upload_name(instance, filename, prefix="resumes")


def avatar_upload_to(instance, filename: str) -> str:
    """`User.avatar` uchun yo'l."""
    return random_upload_name(instance, filename, prefix="avatars")
