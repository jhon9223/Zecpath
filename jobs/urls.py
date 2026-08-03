from django.urls import path

from .views import (
    CreateJobAPIView,
    UpdateJobAPIView,
    JobStatusAPIView,
)

urlpatterns = [
    path(
        "create/",
        CreateJobAPIView.as_view(),
        name="create-job",
    ),

    path(
        "<int:job_id>/update/",
        UpdateJobAPIView.as_view(),
        name="update-job",
    ),

    path(
        "<int:job_id>/status/",
        JobStatusAPIView.as_view(),
        name="job-status",
    ),
]
