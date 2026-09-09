from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogAPIView(generics.ListAPIView):

    serializer_class = AuditLogSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get_queryset(self):
        return AuditLog.objects.select_related(
            "user"
        ).order_by("-created_at")
