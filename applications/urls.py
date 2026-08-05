from django.urls import path

from .views import (
    ApplyJobAPIView,
    MyApplicationsAPIView,
)

urlpatterns = [

    path(
        "<int:job_id>/apply/",
        ApplyJobAPIView.as_view(),
        name="apply-job",
    ),

    path(
        "my-applications/",
        MyApplicationsAPIView.as_view(),
        name="my-applications",
    ),
]
