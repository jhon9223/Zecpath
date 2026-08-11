from django.urls import path

from .views import ResumeParseAPIView


urlpatterns = [
    path(
        "parse/",
        ResumeParseAPIView.as_view(),
        name="resume-parse"
    ),
]
