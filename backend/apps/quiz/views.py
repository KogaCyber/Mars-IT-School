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
    """«Тест» sahifasi uchun savollar va variantlar."""

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
        submission = get_object_or_404(Submission.objects.select_related("outcome"), pk=pk)
        return Response(SubmissionResultSerializer(submission, context={"request": request}).data)
