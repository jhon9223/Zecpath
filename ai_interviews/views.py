from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsEmployer
from jobs.models import Job

from .models import AICall
from .serializers import (
    AIInterviewSessionSerializer,
    CallLogSerializer,
)


class AIInterviewAuditAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user
        )

        calls = AICall.objects.filter(
            application__job=job
        ).select_related(
            "application__candidate__user"
        ).prefetch_related(
            "session__questions__answer",
            "logs"
        ).order_by(
            "-created_at"
        )

        data = []

        for call in calls:

            session_data = None

            if hasattr(call, "session"):
                session_data = AIInterviewSessionSerializer(
                    call.session
                ).data

            data.append({
                "call_id": call.id,
                "application_id": call.application.id,
                "candidate": call.application.candidate.user.username,
                "status": call.status,
                "scheduled_at": call.scheduled_at,
                "attempts": call.attempts,
                "error": call.error,
                "session": session_data,
                "logs": CallLogSerializer(
                    call.logs.all(),
                    many=True
                ).data,
            })

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "total_calls": calls.count(),
            "queued_calls": calls.filter(
                status=AICall.QUEUED
            ).count(),
            "in_progress_calls": calls.filter(
                status=AICall.IN_PROGRESS
            ).count(),
            "completed_calls": calls.filter(
                status=AICall.COMPLETED
            ).count(),
            "failed_calls": calls.filter(
                status=AICall.FAILED
            ).count(),
            "calls": data,
        })
