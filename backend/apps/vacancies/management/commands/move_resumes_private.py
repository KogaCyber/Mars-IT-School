"""Eski rezyumelarni ochiq `MEDIA_ROOT` dan himoyalangan papkaga ko'chiradi.

Bu buyruq bir marta, yangilanishdan keyin ishga tushiriladi:

    python manage.py move_resumes_private

Ilgari rezyumelar `MEDIA_ROOT/resumes/` ichida saqlanardi va WhiteNoise ularni
`/media/resumes/...` manzilida hammaga uzatardi. Endi ular
`PRIVATE_MEDIA_ROOT/resumes/` ga ko'chadi — o'sha manzillar 404 bo'ladi va
fayl faqat admin paneldagi havola orqali ochiladi.
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Rezyume fayllarini ochiq media papkasidan himoyalangan papkaga ko'chiradi."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Faqat nima qilinishini ko'rsatadi, fayllarga tegmaydi.",
        )

    def handle(self, *args, **options) -> None:
        source = Path(settings.MEDIA_ROOT) / "resumes"
        target = Path(settings.PRIVATE_MEDIA_ROOT) / "resumes"
        dry_run = options["dry_run"]

        if not source.exists():
            self.stdout.write("Ochiq papkada rezyume yo'q — ko'chirish shart emas.")
            return

        moved = 0
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue

            destination = target / path.relative_to(source)
            self.stdout.write(f"{path}  →  {destination}")
            if dry_run:
                moved += 1
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            # `move` bir xil diskda oddiy rename — fayl ikki joyda qolmaydi.
            shutil.move(str(path), str(destination))
            moved += 1

        # Bo'shab qolgan papkalarni ham olib tashlaymiz. `rglob("*")` bo'sh
        # papkalarni ham qaytaradi, shuning uchun aynan FAYL qolganini
        # tekshiramiz — aks holda `media/resumes/2026/09/` skeleti qolib
        # ketardi va "ko'chirildimi?" degan savol tug'ilardi.
        if not dry_run and source.exists():
            if any(item.is_file() for item in source.rglob("*")):
                self.stdout.write(
                    self.style.WARNING("Ba'zi fayllar ko'chmadi — papka saqlab qolindi.")
                )
            else:
                shutil.rmtree(source, ignore_errors=True)

        prefix = "Ko'chiriladi" if dry_run else "Ko'chirildi"
        self.stdout.write(self.style.SUCCESS(f"{prefix}: {moved} ta fayl."))
