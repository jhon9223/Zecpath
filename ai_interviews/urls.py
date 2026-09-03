from django.urls import path

from .views import (
    AIInterviewAuditAPIView,
    AIAnswerEvaluationAPIView,
    AIAnswerEvaluationDetailAPIView,
)


urlpatterns = [
    path(
        "jobs/<int:job_id>/audit/",
        AIInterviewAuditAPIView.as_view(),
        name="ai-interview-audit",
    ),
    path(
        "answers/evaluate/",
        AIAnswerEvaluationAPIView.as_view(),
        name="ai-answer-evaluate",
    ),
    path(
        "answers/<int:answer_id>/evaluation/",
        AIAnswerEvaluationDetailAPIView.as_view(),
        name="ai-answer-evaluation-detail",
    ),
]
