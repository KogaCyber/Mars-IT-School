"""JWT autentifikatsiyasi — `session_epoch` da'vosini tekshiradi.

Nega kerak: `RevokedRefreshToken` faqat bizga MA'LUM bo'lgan tokenni bekor
qiladi (chiqishda yoki rotatsiyada). Parol o'zgartirilganda esa vaziyat
boshqacha — foydalanuvchi aynan o'g'irlangan, bizga noma'lum tokenni
o'chirmoqchi bo'ladi. Uni ro'yxatga qo'sha olmaymiz.

Yechim: har bir tokenga foydalanuvchining `session_epoch` qiymati yoziladi.
Parol o'zgarsa raqam oshadi va eski tokenlardagi qiymat mos kelmay qoladi —
ularning hammasi bir vaqtda yaroqsiz bo'ladi.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

#: Token ichidagi da'vo nomi.
EPOCH_CLAIM = "epoch"


def token_epoch_is_current(token_payload, user) -> bool:
    """Tokendagi davr foydalanuvchining joriy davriga mos keladimi."""
    return int(token_payload.get(EPOCH_CLAIM, 0)) == int(user.session_epoch)


class JWTAuthentication(BaseJWTAuthentication):
    """Har bir so'rovda token davri hali amal qilishini tekshiradi."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not token_epoch_is_current(validated_token.payload, user):
            raise InvalidToken("Sessiya yakunlangan. Qaytadan kiring.")
        return user


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """`drf-spectacular` uchun: bu sinf ham oddiy Bearer JWT ishlatadi.

    Kengaytmasiz generator har bir view uchun "could not resolve authenticator"
    ogohlantirishini berardi va API hujjatida «Authorize» tugmasi yo'q edi.
    """

    target_class = "apps.accounts.authentication.JWTAuthentication"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
