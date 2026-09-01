"""Xarita havolasini ikkiga ajratish: Yandex Maps va Google Maps.

Mavjud `map_url` frontendda Yandex havolasi sifatida ishlatilgan
(`BranchMapLinks.vue`), shuning uchun u o'chirilmaydi — nomi o'zgartiriladi
va qiymatlar saqlanib qoladi.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("branches", "0002_branch_working_hours_translations"),
    ]

    operations = [
        migrations.RenameField(
            model_name="branch", old_name="map_url", new_name="map_url_yandex"
        ),
        migrations.AlterField(
            model_name="branch",
            name="map_url_yandex",
            field=models.URLField(
                blank=True,
                help_text="Masalan: https://yandex.uz/maps/?ll=69.240562,41.311081&z=17",
                verbose_name="Yandex Maps havolasi",
            ),
        ),
        migrations.AddField(
            model_name="branch",
            name="map_url_google",
            field=models.URLField(
                blank=True,
                help_text="Masalan: https://www.google.com/maps/@41.311081,69.240562,17z",
                verbose_name="Google Maps havolasi",
            ),
        ),
        migrations.AlterField(
            model_name="branch",
            name="latitude",
            field=models.FloatField(
                blank=True,
                help_text=(
                    "Xaritadagi nishon shu koordinatada turadi. "
                    "Bo'sh qoldirsangiz — havoladan yoki manzildan avtomatik topiladi."
                ),
                null=True,
                verbose_name="kenglik (latitude)",
            ),
        ),
        migrations.AlterField(
            model_name="branch",
            name="longitude",
            field=models.FloatField(blank=True, null=True, verbose_name="uzunlik (longitude)"),
        ),
    ]
