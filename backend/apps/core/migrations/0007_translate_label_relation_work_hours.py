"""`label`, `relation`, `work_hours` maydonlarini tarjimalanadigan qilish.

Mavjud qiymatlar asosiy til (ru) maydoniga ko'chiriladi — shuning uchun
o'chirib-yaratish emas, `RenameField` ishlatilgan.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_sitesettings_work_hours"),
    ]

    operations = [
        # --- SiteSettings.work_hours ---
        migrations.RenameField(
            model_name="sitesettings", old_name="work_hours", new_name="work_hours_ru"
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="work_hours_ru",
            field=models.CharField(
                blank=True,
                help_text="Masalan: Ежедневно с 09:00 до 20:00",
                max_length=120,
                verbose_name="ish vaqti (ru)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="work_hours_uz",
            field=models.CharField(blank=True, max_length=120, verbose_name="ish vaqti (uz)"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="work_hours_en",
            field=models.CharField(blank=True, max_length=120, verbose_name="ish vaqti (en)"),
        ),
        # --- ParentReview.relation ---
        migrations.RenameField(
            model_name="parentreview", old_name="relation", new_name="relation_ru"
        ),
        migrations.AlterField(
            model_name="parentreview",
            name="relation_ru",
            field=models.CharField(
                blank=True,
                help_text="Masalan: Ali ning onasi",
                max_length=120,
                verbose_name="kim (ru)",
            ),
        ),
        migrations.AddField(
            model_name="parentreview",
            name="relation_uz",
            field=models.CharField(blank=True, max_length=120, verbose_name="kim (uz)"),
        ),
        migrations.AddField(
            model_name="parentreview",
            name="relation_en",
            field=models.CharField(blank=True, max_length=120, verbose_name="kim (en)"),
        ),
        # --- ProjectDefenceStep.label ---
        migrations.RenameField(
            model_name="projectdefencestep", old_name="label", new_name="label_ru"
        ),
        migrations.AlterField(
            model_name="projectdefencestep",
            name="label_ru",
            field=models.CharField(
                help_text="Masalan: «1 раз», «34»",
                max_length=32,
                verbose_name="qiymat (ru)",
            ),
        ),
        migrations.AddField(
            model_name="projectdefencestep",
            name="label_uz",
            field=models.CharField(blank=True, max_length=32, verbose_name="qiymat (uz)"),
        ),
        migrations.AddField(
            model_name="projectdefencestep",
            name="label_en",
            field=models.CharField(blank=True, max_length=32, verbose_name="qiymat (en)"),
        ),
    ]
