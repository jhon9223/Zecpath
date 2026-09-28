
from rest_framework import generics, serializers
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
from .services import calculate_application_ats_score, update_application_status
from .automation import auto_process_application, auto_process_job_applications
from .tasks import process_job_applications
from accounts.models import User
from notifications.events import notify_application_submitted
from .services import RecruiterAnalyticsService
# from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import ScopedRateThrottle
from subscriptions.permissions import AdvancedAnalyticsPermission, PremiumRecruiterPermission

from drf_spectacular.utils import extend_schema, OpenApiResponse

# Create your views here.


# Swagger documentation serializers
class ApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            JobApplication.APPLIED,
            JobApplication.SHORTLISTED,
            JobApplication.INTERVIEW,
            JobApplication.REJECTED,
            JobApplication.SELECTED,
        ]
    )


class JobAnalyticsResponseSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    interview = serializers.IntegerField()
    selected = serializers.IntegerField()
    rejected = serializers.IntegerField()


class RankedCandidateSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    candidate = serializers.CharField()
    ats_score = serializers.FloatField(allow_null=True)
    status = serializers.CharField()


class AutoProcessApplicationResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    application_id = serializers.IntegerField()
    ats_score = serializers.FloatField()
    status = serializers.CharField()


class AutoProcessJobResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    job_id = serializers.IntegerField()
    task_id = serializers.CharField()


class PremiumCandidateRankingResponseSerializer(serializers.Serializer):
    premium = serializers.BooleanField()
    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    ranked_candidates = RankedCandidateSerializer(many=True)


class PremiumRecruiterAnalyticsResponseSerializer(serializers.Serializer):
    premium = serializers.BooleanField()
    total_applications = serializers.IntegerField()
    total_shortlisted = serializers.IntegerField()
    total_interviewed = serializers.IntegerField()
    total_selected = serializers.IntegerField()
    conversion_rates = serializers.DictField()
    jobs = serializers.ListField()


class ApplicationErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class ApplyJobAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    @extend_schema(
        summary="Apply for a job",
        description=(
            "Submit an application for an active job. "
            "Duplicate applications are rejected."
        ),
        request=JobApplicationSerializer,
        responses={
            201: JobApplicationSerializer,
            400: OpenApiResponse(
                response=ApplicationErrorResponseSerializer,
                description="Duplicate application or invalid application data.",
            ),
            403: OpenApiResponse(
                description="Permission denied."
            ),
            404: OpenApiResponse(
                description="Candidate profile or active job not found."
            ),
        },
    )
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

    @extend_schema(
        summary="List my applications",
        description="Retrieve the authenticated candidate's job applications.",
        responses={
            200: JobApplicationSerializer(many=True),
            403: OpenApiResponse(description="Permission denied."),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return JobApplication.objects.none()

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

    @extend_schema(
        summary="Update application status",
        description="Update an application's status for a job owned by the authenticated employer.",
        request=ApplicationStatusUpdateSerializer,
        responses={
            200: JobApplicationSerializer,
            400: OpenApiResponse(
                response=ApplicationErrorResponseSerializer,
                description="Invalid application status.",
            ),
            403: OpenApiResponse(
                response=ApplicationErrorResponseSerializer,
                description="You do not own this job or are not authorized.",
            ),
            404: OpenApiResponse(description="Application not found."),
        },
    )
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

        update_application_status(
            application,
            new_status
        )

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

    @extend_schema(
        summary="List applications for a job",
        description="List applications for an employer-owned job. Supports status filtering and candidate username search.",
        responses={
            200: JobApplicationSerializer(many=True),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # Dynamic / depends on user, URL, permissions, etc.:
    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return JobApplication.objects.none()

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

    @extend_schema(
        summary="Get job application analytics",
        description="Retrieve application counts for an employer-owned job.",
        responses={
            200: JobAnalyticsResponseSerializer,
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
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

    @extend_schema(
        summary="Calculate application ATS score",
        description="Calculate and save the ATS score after checking candidate or employer ownership.",
        responses={
            200: OpenApiResponse(
                description="ATS score and scoring details.",
            ),
            403: OpenApiResponse(
                response=ApplicationErrorResponseSerializer,
                description="Access denied.",
            ),
            404: OpenApiResponse(description="Application not found."),
        },
    )
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

    @extend_schema(
        summary="Rank candidates for a job",
        description="Retrieve candidates ranked by their ATS scores for an employer-owned job.",
        responses={
            200: RankedCandidateSerializer(many=True),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
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

    @extend_schema(
        summary="Automatically process an application",
        description="Run the application auto-processing logic using its existing ATS score.",
        request=None,
        responses={
            200: AutoProcessApplicationResponseSerializer,
            400: OpenApiResponse(
                response=ApplicationErrorResponseSerializer,
                description="ATS score is not available.",
            ),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
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

    @extend_schema(
        summary="Start automatic job application processing",
        description="Queue background processing for applications belonging to an employer-owned job.",
        request=None,
        responses={
            200: AutoProcessJobResponseSerializer,
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
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


class RecruiterJobAnalyticsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
    ]

    @extend_schema(
        summary="Get recruiter analytics for a job",
        description="Retrieve funnel analytics for a job owned by the authenticated employer.",
        responses={
            200: OpenApiResponse(description="Job-level recruiter funnel analytics."),
            403: OpenApiResponse(description="Permission denied."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user,
        )

        analytics_service = RecruiterAnalyticsService()

        data = analytics_service.get_job_funnel(job)

        return Response(data)


class RecruiterAnalyticsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
    ]

    @extend_schema(
        summary="Get recruiter analytics overview",
        description="Retrieve overall recruitment funnel analytics for the authenticated employer.",
        responses={
            200: OpenApiResponse(description="Recruiter overview analytics."),
            403: OpenApiResponse(description="Permission denied."),
        },
    )
    def get(self, request):

        jobs = Job.objects.filter(
            employer__user=request.user
        )

        analytics_service = RecruiterAnalyticsService()

        data = analytics_service.get_recruiter_overview(jobs)

        return Response(data)


class PremiumRecruiterAnalyticsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
        AdvancedAnalyticsPermission,
    ]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "premium_feature"

    @extend_schema(
        summary="Get premium recruiter analytics",
        description="Retrieve premium recruitment analytics, including conversion rates and job-level metrics.",
        responses={
            200: PremiumRecruiterAnalyticsResponseSerializer,
            403: OpenApiResponse(description="Permission denied or premium access required."),
        },
    )
    def get(self, request):

        jobs = Job.objects.filter(
            employer__user=request.user
        )

        analytics_service = RecruiterAnalyticsService()

        data = analytics_service.get_recruiter_overview(jobs)

        return Response({
            "premium": True,
            "total_applications": data["total_applications"],
            "total_shortlisted": data["total_shortlisted"],
            "total_interviewed": data["total_interviewed"],
            "total_selected": data["total_selected"],
            "conversion_rates": data["conversion_rates"],
            "jobs": data["jobs"],
        })


class PremiumCandidateRankingAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
        PremiumRecruiterPermission,
    ]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "premium_feature"

    @extend_schema(
        summary="Get premium candidate rankings",
        description="Retrieve ATS-ranked candidates for an employer-owned job with premium recruiter access.",
        responses={
            200: PremiumCandidateRankingResponseSerializer,
            403: OpenApiResponse(description="Permission denied or premium access required."),
            404: OpenApiResponse(description="Job not found."),
        },
    )
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

        return Response({
            "premium": True,
            "job_id": job.id,
            "job_title": job.title,
            "ranked_candidates": data,
        })
