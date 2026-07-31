from django.urls import path
from .views import (
    MyProfileAPIView,
    UpdateProfileAPIView,
    DeleteProfileAPIView,
    ResumeUploadAPIView,
    CandidateProfileListAPIView
)

urlpatterns = [
    path("me/", MyProfileAPIView.as_view(), name="my-profile"),
    path("update/", UpdateProfileAPIView.as_view(), name="update-profile"),
    path("delete/", DeleteProfileAPIView.as_view(), name="delete-profile"),
    path("delete/", DeleteProfileAPIView.as_view(), name="delete-profile"),
    path("upload-resume/", ResumeUploadAPIView.as_view(), name="upload-resume"),
    path("candidates/", CandidateProfileListAPIView.as_view(),
         name="candidate-list",),
]
