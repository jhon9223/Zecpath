from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import LogoutSerializer
from .serializers import ProfileSerializer
from .serializers import AdminActionLogSerializer
from .permissions import (
    IsAdmin,
    IsEmployer,
    IsCandidate,
)
from django.shortcuts import get_object_or_404
from .models import User, AdminActionLog
from profiles.models import CandidateProfile
from applications.models import JobApplication
from jobs.models import Job
from rest_framework import generics
# Create your views here.


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "User created successfully."
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EmployerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request):

        return Response({"message": "Welcome Employer"})


class CandidateDashboardAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get(self, request):

        candidate = get_object_or_404(
            CandidateProfile,
            user=request.user,
            is_deleted=False
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


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": "Welcome Admin"})


class ApproveEmployerAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def patch(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id,
            role=User.EMPLOYER
        )

        user.is_verified = True  # from .models import User

        user.save(update_fields=["is_verified"])
        # "Only update the is_verified column in the database."Instead of potentially saving every changed field on the model, Django is told specifically which field to update.
        AdminActionLog.objects.create(
            admin=request.user,
            action="APPROVED_EMPLOYER",
            target_user=user
        )
        return Response({
            "message": "Employer approved successfully."
        })


class BlockUserAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def patch(self, request, user_id):

        user = get_object_or_404(
            User,
            id=user_id
        )

        user.is_active = False
        user.save(update_fields=["is_active"])
        AdminActionLog.objects.create(
            admin=request.user,
            action="BLOCKED_USER",
            target_user=user
        )
        return Response({
            "message": "User blocked successfully."
        })


class AdminPlatformStatsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def get(self, request):

        from jobs.models import Job
        from applications.models import JobApplication

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
            "total_applications": total_applications
        })


class AdminAuditLogAPIView(generics.ListAPIView):

    serializer_class = AdminActionLogSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def get_queryset(self):
        return AdminActionLog.objects.select_related(
            "admin",
            "target_user"
        ).order_by("-created_at")
