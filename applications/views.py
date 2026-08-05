from rest_framework import generics
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsCandidate

from jobs.models import Job
from profiles.models import CandidateProfile

from .models import JobApplication
from .serializers import JobApplicationSerializer
# Create your views here.


class ApplyJobAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def post(self, request, job_id):

        candidate = get_object_or_404(
            CandidateProfile,
            user=request.user,
            is_deleted=False
        )

        job = get_object_or_404(
            Job,
            id=job_id,
            status=Job.ACTIVE
        )

        if JobApplication.objects.filter(
            candidate=candidate,
            job=job
        ).exists():

            return Response(
                {
                    "error": "You have already applied for this job."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = JobApplicationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                candidate=candidate,
                job=job
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MyApplicationsAPIView(generics.ListAPIView):

    serializer_class = JobApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        candidate = CandidateProfile.objects.get(
            user=self.request.user,
            is_deleted=False
        )

        return JobApplication.objects.filter(
            candidate=candidate
        ).select_related(
            "job"
        ).order_by("-applied_at")
