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

from accounts.permissions import IsEmployer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
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


class UpdateApplicationStatusAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def patch(self, request, application_id):

        application = get_object_or_404(
            JobApplication,
            id=application_id
        )

        # Ownership validation
        if application.job.employer.user != request.user:
            return Response(
                {
                    "error": "You are not allowed to update this application."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get("status")

        valid_statuses = [
            JobApplication.APPLIED,
            JobApplication.SHORTLISTED,
            JobApplication.INTERVIEW,
            JobApplication.REJECTED,
            JobApplication.SELECTED,
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "error": "Invalid status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = new_status
        application.save()

        serializer = JobApplicationSerializer(application)

        return Response(serializer.data)


class JobApplicationsAPIView(generics.ListAPIView):

    serializer_class = JobApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = [
        "status",
    ]

    search_fields = [
        "candidate__user__username",
    ]

    def get_queryset(self):

        job = get_object_or_404(
            Job,
            id=self.kwargs["job_id"],
            employer__user=self.request.user
        )

        return JobApplication.objects.filter(  # here response because its using inbuilt generics class
            job=job
        ).select_related(
            "candidate__user",
            "job"
        ).order_by("-applied_at")


class JobAnalyticsAPIView(APIView):

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

        applications = JobApplication.objects.filter(job=job)

        return Response({

            "total_applications": applications.count(),

            "shortlisted": applications.filter(
                status=JobApplication.SHORTLISTED
            ).count(),

            "interview": applications.filter(
                status=JobApplication.INTERVIEW
            ).count(),

            "selected": applications.filter(
                status=JobApplication.SELECTED
            ).count(),

            "rejected": applications.filter(
                status=JobApplication.REJECTED
            ).count(),

        })
