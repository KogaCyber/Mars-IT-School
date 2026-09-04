from bson import ObjectId
from bson.errors import InvalidId
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Quiz, Submission
from .serializers import (
    QuizSerializer,
    SubmissionCreateSerializer,
    SubmissionResultSerializer,
)
from .services import evaluate


class QuizViewSet(ReadOnlyModelViewSet):
    """«Тест» sahifasi uchun savollar va variantlar.

    Ataylab keshlanmaydi: `sample_questions()` har so'rovda savollarning
    tasodifiy qismini tanlab, variantlarni aralashtiradi. Keshlansa, bir
    daqiqa ichida kelgan hamma foydalanuvchi bir xil testni ko'rardi.
    """

    permission_classes = [AllowAny]
    serializer_class = QuizSerializer
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        return Quiz.objects.published()


class QuizSubmitView(APIView):
    """Javoblarni qabul qilib, «Результаты теста» sahifasi uchun natija qaytaradi."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "lead"
    serializer_class = SubmissionCreateSerializer

    @extend_schema(request=SubmissionCreateSerializer, responses=SubmissionResultSerializer)
    def post(self, request, slug: str):
        quiz = get_object_or_404(Quiz.objects.published(), slug=slug)

        serializer = SubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission = evaluate(quiz, serializer.validated_data["answers"])
        submission.full_name = serializer.validated_data.get("full_name", "")
        submission.phone = serializer.validated_data.get("phone", "")
        # `evaluate()` saqlanmagan obyekt qaytaradi — kontakt maydonlari
        # qo'yilgandan keyin bitta marta yoziladi (ilgari ikki yozuv bo'lardi).
        submission.save()

        return Response(
            SubmissionResultSerializer(submission, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class QuizResultView(APIView):
    """Natija sahifasini havola orqali qayta ochish uchun."""

    permission_classes = [AllowAny]
    serializer_class = SubmissionResultSerializer

    @extend_schema(responses=SubmissionResultSerializer)
    def get(self, request, pk: str):
        # Manzildagi qiymat foydalanuvchidan keladi (havola qo'lda tahrirlanishi
        # mumkin). ObjectId bo'lmasa MongoDB maydoni `ValidationError` ko'tarib
        # 500 berardi — buzuq havola uchun to'g'ri javob esa 404.
        try:
            object_id = ObjectId(str(pk))
        except (InvalidId, TypeError, ValueError) as exc:
            raise Http404("Natija topilmadi.") from exc

        submission = get_object_or_404(
            Submission.objects.select_related("outcome"), pk=object_id
        )
        return Response(SubmissionResultSerializer(submission, context={"request": request}).data)
