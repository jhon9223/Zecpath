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
from .services import calculate_application_ats_score
from .automation import auto_process_application, auto_process_job_applications
from .tasks import process_job_applications
from notifications.events import *
from accounts.models import User
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

            application = serializer.save(
                candidate=candidate,
                job=job
            )

            notify_application_submitted(application)

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

        old_status = application.status

        application.status = new_status
        application.save()

        if (
            new_status == JobApplication.SHORTLISTED
            and old_status != JobApplication.SHORTLISTED
        ):
            notify_application_shortlisted(application)

        elif (
            new_status == JobApplication.REJECTED
            and old_status != JobApplication.REJECTED
        ):
            notify_application_rejected(application)

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

    filterset_fields = [  # Simple filtering → filterset_fields,Custom filtering → filterset_class
        "status",
    ]

    search_fields = [
        "candidate__user__username",
    ]

    # Dynamic / depends on user, URL, permissions, etc.:
    def get_queryset(self):

        job = get_object_or_404(
            Job,
            id=self.kwargs["job_id"],
            employer__user=self.request.user
        )

        return JobApplication.objects.filter(  # here return because its using inbuilt generics class
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


class ApplicationATSScoreAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):

        application = get_object_or_404(
            JobApplication.objects.select_related(
                "job",
                "candidate"
            ),
            id=application_id
        )

        # Candidate can access only their own application.
        if request.user.role == User.CANDIDATE:

            if application.candidate.user != request.user:
                return Response(
                    {
                        "error": "You are not allowed to access this application."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # Employer can access only applications for their own jobs.
        elif request.user.role == User.EMPLOYER:

            if application.job.employer.user != request.user:
                return Response(
                    {
                        "error": "You are not allowed to access this application."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # Other roles are not allowed.
        else:
            return Response(
                {
                    "error": "You are not allowed to access ATS scores."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        result = calculate_application_ats_score(application)

        application.ats_score = result["score"]

        application.save(
            update_fields=["ats_score"]
        )

        return Response(result)


class RankedCandidatesAPIView(APIView):

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

        applications = JobApplication.objects.filter(
            job=job
        ).select_related(
            "candidate",
            # So Django uses double underscore __ to traverse relationships.
            "candidate__user"
        ).order_by("-ats_score")

        data = []

        for application in applications:
            data.append({
                "application_id": application.id,
                "candidate": application.candidate.user.username,
                "ats_score": application.ats_score,
                "status": application.status,
            })

        return Response(data)


class AutoProcessApplicationAPIView(APIView):  # for application

    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, application_id):

        application = get_object_or_404(
            JobApplication,
            id=application_id,
            job__employer__user=request.user
        )

        if application.ats_score is None:
            return Response(
                {"error": "ATS score is not available."},
                status=400
            )

        auto_process_application(application)

        return Response({
            "message": "Application processed successfully.",
            "application_id": application.id,
            "ats_score": application.ats_score,
            "status": application.status
        })

# without celery
# class AutoProcessJobAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     def patch(self, request, job_id):

#         processed = auto_process_job_applications(job_id)

#         return Response({
#             "message": "Applications processed successfully.",
#             "job_id": job_id,
#             "processed": processed
#         })


# with celerey
class AutoProcessJobAPIView(APIView):

    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, job_id):
        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user
        )
        task = process_job_applications.delay(job_id)

        return Response({
            "message": "Application processing started.",
            "job_id": job_id,
            "task_id": task.id
        })
