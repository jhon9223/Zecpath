from django.urls import path

from .views import AuditLogAPIView


urlpatterns = [
    path(
        "logs/",
        AuditLogAPIView.as_view(),
        name="audit-logs",
    ),
]
