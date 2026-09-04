from django.urls import path

from .views import (
    AIInterviewAuditAPIView,
    AIAnswerEvaluationAPIView,
    AIAnswerEvaluationDetailAPIView,
    AvailableSlotsAPIView,
    InterviewScheduleAPIView,
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

    path(
        "jobs/<int:job_id>/slots/",
        AvailableSlotsAPIView.as_view(),
        name="available-slots"
    ),

    path(
        "schedule/",
        InterviewScheduleAPIView.as_view(),
        name="interview-schedule"
    ),
]
