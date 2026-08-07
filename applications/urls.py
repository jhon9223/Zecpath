from django.urls import path

from .views import (
    ApplyJobAPIView,
    MyApplicationsAPIView,
    UpdateApplicationStatusAPIView,
    JobApplicationsAPIView,
    JobAnalyticsAPIView,
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
    path(
        "job/<int:job_id>/applications/",
        JobApplicationsAPIView.as_view(),
        name="job-applications",
    ),

    path(
        "job/<int:job_id>/analytics/",
        JobAnalyticsAPIView.as_view(),
        name="job-analytics",
    ),

]
