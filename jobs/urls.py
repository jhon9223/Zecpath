from django.urls import path

from .views import (
    CreateJobAPIView,
    UpdateJobAPIView,
    JobStatusAPIView,
    JobListAPIView,
    LatestJobListAPIView,
    FeaturedJobListAPIView,
    MyJobsAPIView,


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

]
