"""Sozlamalar — hammasi muhit o'zgaruvchilaridan (`.env` faylidan ham o'qiladi).

Ikki baza:
  * `DATABASE_URL`     — saytning O'Z bazasi (yozamiz): PG 17, `mars_it_school`.
  * `LMS_DATABASE_URL` — gamification (LMS) bazasi, FAQAT O'QISH uchun. Rol
    `school_ro` faqat to'rt jadvalga SELECT huquqiga ega — sayt LMS'ga yoza
    olmaydi, hatto xato bo'lsa ham.
"""

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

    # --- Tahrirlash (2-bosqich) ---
    secret_key: str = "change-me"
    debug: bool = False

    languages: tuple[str, ...] = ("ru", "uz", "en")
    default_language: str = "ru"

    @property
    def lms_enabled(self) -> bool:
        return bool(self.lms_database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
