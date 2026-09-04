"""Test natijasi havolasi uchun taxmin qilib bo'lmaydigan kalit.

Ilgari natija sahifasi MongoDB `_id` si orqali ochilardi. ObjectId — vaqt
tamg'asi + mashina identifikatori + ketma-ket hisoblagich, ya'ni bitta
havolani bilgan odam boshqa foydalanuvchilarning natijalarini ham taxmin
qila olardi (IDOR / enumeration).

Migratsiya uch bosqichda bajariladi, chunki `unique=True` maydonni to'g'ridan
to'g'ri qo'shib bo'lmaydi: mavjud hujjatlarning hammasida qiymat bir xil
(bo'sh) bo'lib qolardi va unikal indeks yaratilmasdi.

  1. Maydon unikal bo'lmagan holda qo'shiladi.
  2. Har bir mavjud yozuvga ALOHIDA tasodifiy qiymat yoziladi.
  3. Maydon unikal indeksga o'tkaziladi.
"""

import apps.quiz.models
from django.db import migrations, models


def fill_tokens(apps_registry, schema_editor):
    """Mavjud har bir topshiriqqa o'z kalitini beradi."""
    Submission = apps_registry.get_model("quiz", "Submission")
    for submission in Submission.objects.filter(public_token="").iterator():
        submission.public_token = apps.quiz.models.new_public_token()
        submission.save(update_fields=["public_token"])


def noop(apps_registry, schema_editor):
    """Orqaga qaytishda hech narsa qilinmaydi — maydon baribir o'chiriladi."""


class Migration(migrations.Migration):
    dependencies = [
        ("quiz", "0003_option_skill_submission_skills"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="public_token",
            field=models.CharField(
                db_index=True,
                default="",
                editable=False,
                max_length=64,
                verbose_name="havola kaliti",
            ),
        ),
        migrations.RunPython(fill_tokens, noop),
        migrations.AlterField(
            model_name="submission",
            name="public_token",
            field=models.CharField(
                db_index=True,
                default=apps.quiz.models.new_public_token,
                editable=False,
                max_length=64,
                unique=True,
                verbose_name="havola kaliti",
            ),
        ),
    ]
