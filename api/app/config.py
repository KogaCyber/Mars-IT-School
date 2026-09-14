"""Sozlamalar — hammasi muhit o'zgaruvchilaridan (`.env` faylidan ham o'qiladi).

Ikki baza:
  * `DATABASE_URL`     — saytning O'Z bazasi (yozamiz): PG 17, `mars_it_school`.
  * `LMS_DATABASE_URL` — gamification (LMS) bazasi, FAQAT O'QISH uchun. Rol
    `school_ro` faqat to'rt jadvalga SELECT huquqiga ega — sayt LMS'ga yoza
    olmaydi, hatto xato bo'lsa ham.
"""

import re
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    # --- Baza ---
    database_url: str = "postgresql+asyncpg://mars_it_school:mars_it_school@localhost:5432/mars_it_school"
    lms_database_url: str = ""  # bo'sh bo'lsa LMS'dan o'qish o'chadi (lokal ishlab chiqish)

    # --- Manzillar ---
    # Sayt domen ildizida emas, `/school/` yo'lida turadi. Proksi prefiksni kesib
    # uzatadi; bu qiymat javoblardagi to'liq manzillar (rasm URL'lari) uchun.
    root_path: str = ""
    site_url: str = "http://localhost:5173"
    public_media_url: str = "/media/"

    # --- Fayllar ---
    media_root: Path = BASE_DIR / "media"
    private_media_root: Path = BASE_DIR / "private-media"  # rezyumelar — hech qachon statik uzatilmaydi
    max_upload_bytes: int = 5 * 1024 * 1024

    # --- Kesh / cheklovlar ---
    redis_url: str = ""
    public_cache_seconds: int = 60
    lead_rate_per_hour: int = 40
    num_proxies: int = 1  # Caddy -> nginx -> uvicorn = 2 (mars)

    # --- Xabarlar ---
    lead_notify_emails: list[str] = Field(default_factory=list)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    default_from_email: str = "Mars IT School <no-reply@marsit.uz>"

    # --- Muharrir: Mars ID (OIDC) orqali kirish -----------------------------
    # Mars ID — maktab ekotizimining SSO'si (id.marshub.uz). Sayt uchun alohida
    # OAuth-klient `school-site` ro'yxatdan o'tkazilgan (mars-id/server.js).
    # Muharrirga kim kiradi: `is_staff` (LMS xodimi) yoki `role == admin`.
    marsid_issuer: str = "https://id.marshub.uz"
    marsid_client_id: str = "school-site"
    marsid_client_secret: str = ""
    # Muharrirga kim kiradi. Bo'sh bo'lsa — eski xatti-harakat (har qanday
    # `is_staff`/`admin`). To'ldirilsa — FAQAT shu ro'yxatdagilar, qolganlar rad.
    # Har bir yozuv — Mars ID `sub` (o'zgarmas, eng ishonchli), `handle`, yoki
    # TASDIQLANGAN email. Vergul/probel bilan ajratiladi, `@` va katta-kichik
    # harf ahamiyatsiz. Masalan:
    #   EDITOR_ALLOWLIST=@south67, ivan@marsit.uz, 6f2c1a90-...
    editor_allowlist: str = ""
    # Sessiya cookie'si va `state` imzosi uchun kalit. Bo'sh — muharrir o'chiq.
    secret_key: str = "change-me"
    editor_session_hours: int = 12
    editor_cookie_name: str = "school_editor"
    debug: bool = False

    languages: tuple[str, ...] = ("ru", "uz", "en")
    default_language: str = "ru"

    @property
    def lms_enabled(self) -> bool:
        return bool(self.lms_database_url)

    @property
    def editor_enabled(self) -> bool:
        return bool(self.marsid_client_secret) and self.secret_key != "change-me"

    @property
    def editor_allowlist_set(self) -> set[str]:
        """Ruxsat etilgan handle/email'lar — normallashtirilgan (`@` yo'q, kichik)."""
        return {p.strip().lstrip("@").lower() for p in re.split(r"[,\s]+", self.editor_allowlist) if p.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
