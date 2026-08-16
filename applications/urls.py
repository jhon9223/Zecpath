from django.urls import path

from .views import (
    ApplyJobAPIView,
    MyApplicationsAPIView,
    UpdateApplicationStatusAPIView,
    JobApplicationsAPIView,
    JobAnalyticsAPIView,
    ApplicationATSScoreAPIView,
    RankedCandidatesAPIView,
    AutoProcessApplicationAPIView,
    AutoProcessJobAPIView,

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
    path(
        "<int:application_id>/ats-score/",
        ApplicationATSScoreAPIView.as_view(),
        name="application-ats-score"
    ),
    path(
        "job/<int:job_id>/ranked-candidates/",
        RankedCandidatesAPIView.as_view(),
        name="ranked-candidates"
    ),
    path(
        "<int:application_id>/auto-process/",
        AutoProcessApplicationAPIView.as_view(),
        name="auto-process-application"
    ),
    path(
        "job/<int:job_id>/auto-process/",
        AutoProcessJobAPIView.as_view(),
        name="auto-process-job"
    ),
]
