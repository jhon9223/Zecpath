from django.urls import path

from .views import AIInterviewAuditAPIView


urlpatterns = [
    path(
        "jobs/<int:job_id>/audit/",
        AIInterviewAuditAPIView.as_view(),
        name="ai-interview-audit"
    ),
]
