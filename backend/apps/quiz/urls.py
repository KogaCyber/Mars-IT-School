from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuizResultView, QuizSubmitView, QuizViewSet

router = DefaultRouter()
router.register("quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    path("quizzes/<slug:slug>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    # Manzilda `Submission.public_token` (URL-safe base64, 43 belgi).
    path("quiz-results/<str:token>/", QuizResultView.as_view(), name="quiz-result"),
    path("", include(router.urls)),
]
