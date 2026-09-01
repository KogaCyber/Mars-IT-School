"""Proforientatsiya testining savollar bazasini yaratadi/to'ldiradi.

Ishlatish:  python manage.py seed_quiz
            python manage.py seed_quiz --reset   # bazani qaytadan yig'ish

Buyruq idempotent: mavjud savollar tegilmaydi, faqat yetishmaydiganlari
qo'shiladi. Shu sababli uni production'da ham xavfsiz ishga tushirish mumkin.
"""

from django.core.management.base import BaseCommand

from apps.quiz.seeding import ensure_quiz


class Command(BaseCommand):
    help = "Proforientatsiya testi uchun savollar bazasini yaratadi."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Eski savollar va natijalarni o'chirib, bazani qaytadan yig'adi.",
        )

    def handle(self, *args, **options) -> None:
        quiz = ensure_quiz(reset=options["reset"])
        total = quiz.questions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Test tayyor: {total} ta savol, urinishda {quiz.questions_per_attempt} tasi "
                f"tasodifiy ko'rsatiladi."
            )
        )
