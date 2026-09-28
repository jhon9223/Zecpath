
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from config.api_schemas import (
    MESSAGE_RESPONSE,
    DashboardStatsSerializer,
    PlatformStatsSerializer,
)

from .models import User, AdminActionLog
from .permissions import IsAdmin, IsEmployer, IsCandidate
from .serializers import (
    SignupSerializer,
    LogoutSerializer,
    ProfileSerializer,
    AdminActionLogSerializer,
)

from profiles.models import CandidateProfile
from applications.models import JobApplication
from jobs.models import Job


class LoginThrottle(AnonRateThrottle):
    scope = "login"


@extend_schema(
    summary="Obtain JWT tokens",
    description=(
        "Authenticate with the user's credentials to obtain "
        "an access token and a refresh token."
    ),
)
class LoginAPIView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SignupSerializer,
        responses={
            201: MESSAGE_RESPONSE,
            400: OpenApiResponse(
                description="Invalid signup data"
            ),
        },
        summary="Register a new user",
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "User created successfully."},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: MESSAGE_RESPONSE,
            400: OpenApiResponse(
                description="Invalid refresh token"
            ),
        },
        summary="Log out a user",
        description=(
            "Submit the refresh token to invalidate it "
            "according to the configured token blacklist flow."
        ),
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer},
        summary="Get the authenticated user's profile",
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class EmployerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    @extend_schema(
        responses={200: MESSAGE_RESPONSE},
        summary="Get the employer dashboard",
    )
    def get(self, request):
        return Response({"message": "Welcome Employer"})


class CandidateDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    @extend_schema(
        operation_id="candidate_dashboard_nested_retrieve",
        responses={200: DashboardStatsSerializer},
        summary="Get candidate dashboard statistics",
    )
    def get(self, request):
        candidate = get_object_or_404(
            CandidateProfile,
            user=request.user,
            is_deleted=False,
        )

        applications = JobApplication.objects.filter(
            candidate=candidate
        )

        return Response({
            "applied_jobs": applications.count(),
            "shortlisted": applications.filter(
                status=JobApplication.SHORTLISTED
            ).count(),
            "interviews": applications.filter(
                status=JobApplication.INTERVIEW
            ).count(),
            "selected": applications.filter(
                status=JobApplication.SELECTED
            ).count(),
            "rejected": applications.filter(
                status=JobApplication.REJECTED
            ).count(),
        })


class LegacyCandidateDashboardAPIView(CandidateDashboardAPIView):

    @extend_schema(
        operation_id="candidate_dashboard_legacy_retrieve",
        responses={200: DashboardStatsSerializer},
        summary="Get candidate dashboard statistics (legacy URL)",
        description=(
            "Legacy URL for candidate dashboard statistics. "
            "Returns the same data as the nested candidate dashboard endpoint."
        ),
    )
    def get(self, request):
        return super().get(request)


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={200: MESSAGE_RESPONSE},
        summary="Get the admin dashboard",
    )
    def get(self, request):
        return Response({"message": "Welcome Admin"})


class ApproveEmployerAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=None,
        responses={200: MESSAGE_RESPONSE},
        summary="Approve an employer",
        description=(
            "Marks the specified employer as verified and "
            "records the action in the admin audit log."
        ),
    )
    def patch(self, request, user_id):
        user = get_object_or_404(
            User,
            id=user_id,
            role=User.EMPLOYER,
        )

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        AdminActionLog.objects.create(
            admin=request.user,
            action="APPROVED_EMPLOYER",
            target_user=user,
        )

        return Response({
            "message": "Employer approved successfully."
        })


class BlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        request=None,
        responses={200: MESSAGE_RESPONSE},
        summary="Block a user",
        description=(
            "Deactivates the specified user and records "
            "the action in the admin audit log."
        ),
    )
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        user.is_active = False
        user.save(update_fields=["is_active"])

        AdminActionLog.objects.create(
            admin=request.user,
            action="BLOCKED_USER",
            target_user=user,
        )

        return Response({
            "message": "User blocked successfully."
        })


class AdminPlatformStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        responses={200: PlatformStatsSerializer},
        summary="Get platform statistics",
    )
    def get(self, request):
        total_users = User.objects.count()

        total_candidates = User.objects.filter(
            role=User.CANDIDATE
        ).count()

        total_employers = User.objects.filter(
            role=User.EMPLOYER
        ).count()

        total_jobs = Job.objects.count()

        active_jobs = Job.objects.filter(
            status=Job.ACTIVE
        ).count()

        total_applications = JobApplication.objects.count()

        return Response({
            "total_users": total_users,
            "total_candidates": total_candidates,
            "total_employers": total_employers,
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
        })


@extend_schema(
    summary="List admin audit logs",
    description=(
        "Returns admin audit records ordered from newest to oldest. "
        "Requires administrator authentication."
    ),
)
class AdminAuditLogAPIView(generics.ListAPIView):
    serializer_class = AdminActionLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return AdminActionLog.objects.select_related(
            "admin",
            "target_user",
        ).order_by("-created_at")
