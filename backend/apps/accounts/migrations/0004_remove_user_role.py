"""`role` maydonini olib tashlaydi.

Maydon hech qanday mantiqda ishlatilmasdi: admin panelga kirishni Django'ning
`is_staff` bayrog'i hal qilardi. Ikkita parallel «haqiqat» esa ziddiyatga olib
kelgandi — bazada `role="admin"` deb turgan, lekin `is_staff=False` bo'lgani
uchun panelga kira olmaydigan hisob bor edi.

Maydonni shunchaki o'chirib yuborish o'sha niyatni yo'qotardi, shuning uchun
avval `role="admin"` bo'lganlar xodim qilib belgilanadi.
"""

from django.db import migrations

ADMIN_ROLE = "admin"


def promote_admins_to_staff(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role=ADMIN_ROLE, is_staff=False).update(is_staff=True)


def restore_roles(apps, schema_editor):
    """Orqaga qaytarish — xodimlar «administrator» rolini qaytarib oladi.

    O'quvchi/o'qituvchi rollarini tiklab bo'lmaydi (ular saqlanmagan), lekin
    bu loyihada bunday hisob umuman bo'lmagan.
    """
    User = apps.get_model("accounts", "User")
    User.objects.filter(is_staff=True).update(role=ADMIN_ROLE)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_avatar"),
    ]

    operations = [
        # Tartib muhim: maydon o'chirilgach undan o'qib bo'lmaydi.
        migrations.RunPython(promote_admins_to_staff, restore_roles),
        migrations.RemoveField(
            model_name="user",
            name="role",
        ),
    ]
