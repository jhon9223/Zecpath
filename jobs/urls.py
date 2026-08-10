from django.urls import path

from .views import (
    CreateJobAPIView,
    UpdateJobAPIView,
    JobStatusAPIView,
    JobListAPIView,
    LatestJobListAPIView,
    FeaturedJobListAPIView,
    MyJobsAPIView,
    SaveJobAPIView,
    MySavedJobsAPIView,
    RecommendedJobsAPIView,
    AdminManageJobAPIView,



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
    path(
        "",
        JobListAPIView.as_view(),
        name="job-list",
    ),
    path(
        "latest/",
        LatestJobListAPIView.as_view(),
        name="latest-jobs",
    ),
    path(
        "featured/",
        FeaturedJobListAPIView.as_view(),
        name="featured-jobs",
    ),
    path(
        "my-jobs/",
        MyJobsAPIView.as_view(),
        name="my-jobs",
    ),
    path(
        "<int:job_id>/save/",
        SaveJobAPIView.as_view(),
        name="save-job",
    ),

    path(
        "my-saved-jobs/",
        MySavedJobsAPIView.as_view(),
        name="my-saved-jobs",
    ),
    path(
        "recommended/",
        RecommendedJobsAPIView.as_view(),
        name="recommended-jobs",
    ),
    path(
        "admin/jobs/<int:job_id>/remove/",
        AdminManageJobAPIView.as_view(),
        name="admin-remove-job",
    ),

]
