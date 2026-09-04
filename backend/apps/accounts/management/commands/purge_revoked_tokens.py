"""Muddati o'tgan bekor qilingan tokenlarni bazadan tozalaydi.

Tozalash `tokens.revoke()` ichida o'z-o'zidan ham bo'ladi; bu buyruq
qo'lda yoki cron orqali darhol tozalash kerak bo'lganda ishlatiladi:
    python manage.py purge_revoked_tokens
"""

from django.core.management.base import BaseCommand

from apps.accounts.tokens import purge_expired


class Command(BaseCommand):
    help = "Muddati o'tgan bekor qilingan refresh tokenlarni o'chiradi."

    def handle(self, *args, **options) -> None:
        deleted = purge_expired()
        self.stdout.write(self.style.SUCCESS(f"O'chirildi: {deleted} ta token."))
