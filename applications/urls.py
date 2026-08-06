from django.urls import path

from .views import (
    ApplyJobAPIView,
    MyApplicationsAPIView,
    UpdateApplicationStatusAPIView,
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
    path(
        "<int:application_id>/status/",
        UpdateApplicationStatusAPIView.as_view(),
        name="update-application-status",
    ),

]
