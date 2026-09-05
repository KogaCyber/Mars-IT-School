"""Admin paneldagi «Foydalanuvchilar» bo'limi.

Bu ro'yxat — admin panelga kira oladigan xodimlar ro'yxati, boshqa hech kim
emas. Saytda o'quvchi yoki o'qituvchi kabineti yo'q, shuning uchun bu yerda
rol tanlash ham, huquq guruhlari ham ko'rinmaydi: kirish huquqini yagona
`is_staff` bayrog'i hal qiladi.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "full_name", "phone", "is_active", "is_superuser", "date_joined")
    list_filter = ("is_active", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "phone")
    readonly_fields = ("date_joined", "last_login", "created_at", "updated_at")

    # `groups` va `user_permissions` ataylab yo'q. Maktab panelida bir necha
    # xodim ishlaydi va ularning hammasiga bir xil huquq kerak — guruhlar
    # faqat chalkashtirardi (`auth.Group` menyudan ham olib tashlangan,
    # `apps/core/admin.py`).
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Shaxsiy ma'lumot"), {"fields": ("first_name", "last_name", "phone", "avatar")}),
        (
            _("Huquqlar"),
            {
                "fields": ("is_active", "is_superuser"),
                "description": _(
                    "Bu ro'yxatdagi har bir foydalanuvchi admin panelga kira oladi. "
                    "«To'liq huquq» belgilansa — barcha bo'limlarni cheklovsiz "
                    "boshqara oladi."
                ),
            },
        ),
        (_("Sanalar"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """Faqat admin panelga kira oladiganlar ko'rsatiladi.

        Ro'yxat «kim panelga kira oladi» degan savolga javob berishi kerak.
        Kira olmaydigan hisoblar bu yerda turса, ro'yxat shu savolga javob
        bermay qo'yadi.
        """
        return super().get_queryset(request).filter(is_staff=True)

    def save_model(self, request, obj, form, change):
        """Bu yerda yaratilgan har bir foydalanuvchi — panel xodimi.

        Ilgari `is_staff` ni qo'lda belgilash kerak edi va u unutilganda
        yangi hisob jimgina yaroqsiz bo'lib qolardi: «administrator» deb
        yaratilgan odam kirishga urinib, sababini tushunmasdi.
        """
        obj.is_staff = True
        super().save_model(request, obj, form, change)
