"""Sahifa bo'limlarini reestr bo'yicha yaratadi/yangilaydi."""

from django.core.management.base import BaseCommand

from apps.core.section_sync import sync_sections


class Command(BaseCommand):
    help = "Sayt sahifalari bo'limlarini (PageSection) reestr bo'yicha sinxronlaydi."

    def handle(self, *args, **options):
        result = sync_sections(stdout=self.stdout)
        self.stdout.write(
            self.style.SUCCESS(
                f"Tayyor: {result['created']} ta yangi bo'lim, "
                f"{result['updated']} ta yangilandi."
            )
        )
