"""Filial ish vaqtini tarjimalanadigan qilish (mavjud qiymat ru ga ko'chadi)."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("branches", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="branch", old_name="working_hours", new_name="working_hours_ru"
        ),
        migrations.AlterField(
            model_name="branch",
            name="working_hours_ru",
            field=models.CharField(blank=True, max_length=160, verbose_name="ish vaqti (ru)"),
        ),
        migrations.AddField(
            model_name="branch",
            name="working_hours_uz",
            field=models.CharField(blank=True, max_length=160, verbose_name="ish vaqti (uz)"),
        ),
        migrations.AddField(
            model_name="branch",
            name="working_hours_en",
            field=models.CharField(blank=True, max_length=160, verbose_name="ish vaqti (en)"),
        ),
    ]
