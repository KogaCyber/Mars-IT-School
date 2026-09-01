"""Muddati o'tgan bekor qilingan tokenlarni bazadan tozalaydi.

Cron/Railway scheduled job sifatida kuniga bir marta ishga tushirish tavsiya etiladi:
    python manage.py purge_revoked_tokens
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import RevokedRefreshToken


class Command(BaseCommand):
    help = "Muddati o'tgan bekor qilingan refresh tokenlarni o'chiradi."

    def handle(self, *args, **options) -> None:
        deleted, _ = RevokedRefreshToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        self.stdout.write(self.style.SUCCESS(f"O'chirildi: {deleted} ta token."))
