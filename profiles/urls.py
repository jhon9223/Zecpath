from django.urls import path
from .views import (
    MyProfileAPIView,
    UpdateProfileAPIView,
    DeleteProfileAPIView,
)

urlpatterns = [
    path("me/", MyProfileAPIView.as_view(), name="my-profile"),
    path("update/", UpdateProfileAPIView.as_view(), name="update-profile"),
    path("delete/", DeleteProfileAPIView.as_view(), name="delete-profile"),
    path("delete/", DeleteProfileAPIView.as_view(), name="delete-profile"),
]
