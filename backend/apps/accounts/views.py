"""Autentifikatsiya API'lari."""

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from .serializers import (
    PasswordChangeSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)
from .tokens import revoke

User = get_user_model()


class LoginView(TokenObtainPairView):
    """Email/telefon + parol orqali JWT olish."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RegisterView(generics.CreateAPIView):
    """Ro'yxatdan o'tish.

    Saytda ro'yxatdan o'tish sahifasi yo'q, shuning uchun bu manzil standart
    bo'yicha YOPIQ (`PUBLIC_REGISTRATION_ENABLED = False`). Ochiq qolsa u
    faqat spam hisob yaratish uchun ishlatilardi. O'quvchi kabineti
    qo'shilganda sozlama yoqiladi.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        if not settings.PUBLIC_REGISTRATION_ENABLED:
            raise PermissionDenied("Ro'yxatdan o'tish hozircha yopiq.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutView(APIView):
    """Refresh tokenni bekor qilinganlar ro'yxatiga qo'shadi.

    `AllowAny` ataylab: access token muddati 15 daqiqa va u tugagach
    foydalanuvchi chiqa olmay qolardi — ya'ni refresh token bekor qilinmasdan
    brauzerda yotib qolardi. Bu yerda haqiqiy "kalit" — refresh tokenning
    o'zi: uni bilgan odam baribir uning egasi.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
    serializer_class = LogoutSerializer

    @extend_schema(request=LogoutSerializer, responses={205: None})
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "refresh token yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            revoke(RefreshToken(refresh))
        except TokenError:
            return Response({"detail": "Token yaroqsiz."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @extend_schema(request=PasswordChangeSerializer, responses={200: OpenApiResponse()})
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Parol yangilandi."})


class TokenRefreshView(BaseTokenRefreshView):
    """Bekor qilingan tokenlarni tekshiradigan yangilash endpoint'i."""

    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]
