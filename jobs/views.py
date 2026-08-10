from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsEmployer, IsCandidate, IsAdmin
from rest_framework.permissions import IsAuthenticated

from .models import Job
from .serializers import JobSerializer

from profiles.models import EmployerProfile, CandidateProfile
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .pagination import JobPagination
from .filters import JobFilter
from django.shortcuts import get_object_or_404
from .models import Job, SavedJob
# Create your views here.


class CreateJobAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request):

        employer = EmployerProfile.objects.get(
            user=request.user,
            is_deleted=False
        )

        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(
                employer=employer
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UpdateJobAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, job_id):

        try:
            job = Job.objects.get(id=job_id)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if job.employer.user != request.user:
            return Response(
                {"error": "You cannot edit this job."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = JobSerializer(
            job,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class JobStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, job_id):

        try:
            job = Job.objects.get(id=job_id)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if job.employer.user != request.user:
            return Response(
                {"error": "You cannot update this job."},
                status=status.HTTP_403_FORBIDDEN
            )

        status_value = request.data.get("status")

        if status_value not in ["ACTIVE", "INACTIVE"]:
            return Response(
                {"error": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = status_value
        job.save()

        return Response(
            {"message": "Job status updated successfully."}
        )


class JobListAPIView(generics.ListAPIView):

    serializer_class = JobSerializer

    queryset = Job.objects.filter(  # Static / same basic data for everyone:
        status=Job.ACTIVE
    ).select_related("employer")

    pagination_class = JobPagination

    filter_backends = [
        DjangoFilterBackend,  # just keep as as format/syntax if you use django filte only add DjangoFilterBackend and search_filter if search filter only
        SearchFilter,
    ]

    filterset_class = JobFilter  # Custom filtering → filterset_class

    search_fields = [
        "title",
        "description",
        "skills",
        "location",
    ]  # ?location=Bangalore works because django-filter matches the query parameter name to the field name.?search=Python works because SearchFilter always looks for the search parameter and checks every field you've listed in search_fields.


class LatestJobListAPIView(generics.ListAPIView):
    serializer_class = JobSerializer

    queryset = Job.objects.filter(
        status=Job.ACTIVE
    ).select_related("employer").order_by("-created_at")[:10]


class FeaturedJobListAPIView(generics.ListAPIView):
    serializer_class = JobSerializer

    queryset = Job.objects.filter(
        status=Job.ACTIVE
    ).select_related("employer").order_by("-created_at")[:5]

# not mentioned in day 19 task created my own...


class MyJobsAPIView(generics.ListAPIView):

    serializer_class = JobSerializer

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    pagination_class = JobPagination

    # Dynamic / depends on user, URL, permissions, etc.:
    def get_queryset(self):

        return Job.objects.filter(
            employer__user=self.request.user
        ).select_related(
            "employer"
        ).order_by("-created_at")


class SaveJobAPIView(APIView):

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

        saved_job, created = SavedJob.objects.get_or_create(  # saved_job → the object that was found or created,created   → True or False
            candidate=candidate,
            job=job
        )

        if not created:
            return Response(
                {"message": "Job already saved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Job saved successfully."},
            status=status.HTTP_201_CREATED
        )


class MySavedJobsAPIView(generics.ListAPIView):

    serializer_class = JobSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        return Job.objects.filter(
            saved_by__candidate__user=self.request.user,
            status=Job.ACTIVE
        ).select_related(
            "employer"
        ).order_by("-created_at")


class RecommendedJobsAPIView(generics.ListAPIView):

    serializer_class = JobSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        candidate = get_object_or_404(
            CandidateProfile,
            user=self.request.user,
            is_deleted=False
        )

        if not candidate.skills:
            return Job.objects.none()

        jobs = Job.objects.filter(
            status=Job.ACTIVE
        ).select_related("employer")

        candidate_skills = [
            skill.strip().lower()
            for skill in candidate.skills.split(",")
        ]

        matching_jobs = []

        for job in jobs:

            job_skills = [
                skill.strip().lower()
                for skill in job.skills.split(",")
            ]

            if any(
                skill in job_skills
                for skill in candidate_skills
            ):
                matching_jobs.append(job.id)

        return Job.objects.filter(
            id__in=matching_jobs
        ).select_related("employer")


class AdminManageJobAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def patch(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id
        )

        job.status = Job.INACTIVE
        job.save(update_fields=["status"])

        return Response({
            "message": "Job removed successfully."
        })
