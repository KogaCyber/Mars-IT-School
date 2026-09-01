"""Galereya izohini tarjimalanadigan qilish (mavjud qiymat ru ga ko'chadi)."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="newsimage", old_name="caption", new_name="caption_ru"
        ),
        migrations.AlterField(
            model_name="newsimage",
            name="caption_ru",
            field=models.CharField(blank=True, max_length=200, verbose_name="izoh (ru)"),
        ),
        migrations.AddField(
            model_name="newsimage",
            name="caption_uz",
            field=models.CharField(blank=True, max_length=200, verbose_name="izoh (uz)"),
        ),
        migrations.AddField(
            model_name="newsimage",
            name="caption_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="izoh (en)"),
        ),
    ]
