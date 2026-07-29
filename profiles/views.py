from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from accounts.models import User
from accounts.permissions import IsAdmin, IsCandidate

from .models import CandidateProfile, EmployerProfile
from .serializers import (
    CandidateProfileSerializer,
    EmployerProfileSerializer,
)
from django.shortcuts import get_object_or_404


class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role == User.CANDIDATE:
            # Get the candidate profile for the authenticated user
            # Use get_object_or_404 to handle the case where the profile does not exist
            profile = get_object_or_404(
                CandidateProfile,
                user=request.user,
                is_deleted=False
            )
            serializer = CandidateProfileSerializer(profile)

        elif request.user.role == User.EMPLOYER:
            profile = EmployerProfile.objects.get(
                user=request.user,
                is_deleted=False
            )
            serializer = EmployerProfileSerializer(profile)

        else:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(serializer.data)


class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):

        if request.user.role == User.CANDIDATE:
            profile = CandidateProfile.objects.get(
                user=request.user,
                is_deleted=False
            )
            serializer = CandidateProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

        elif request.user.role == User.EMPLOYER:
            profile = EmployerProfile.objects.get(
                user=request.user,
                is_deleted=False
            )
            serializer = EmployerProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

        else:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        if request.user.role == User.CANDIDATE:
            profile = CandidateProfile.objects.get(
                user=request.user,
                is_deleted=False
            )

        elif request.user.role == User.EMPLOYER:
            profile = EmployerProfile.objects.get(
                user=request.user,
                is_deleted=False
            )

        else:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.is_deleted = True
        profile.save()

        return Response(
            {"message": "Profile deleted successfully"},
            status=status.HTTP_200_OK
        )


class AdminProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, user_id):

        try:
            user = User.objects.get(id=user_id)

            if user.role == User.CANDIDATE:
                profile = CandidateProfile.objects.get(
                    user=user,
                    is_deleted=False
                )
                serializer = CandidateProfileSerializer(profile)

            elif user.role == User.EMPLOYER:
                profile = EmployerProfile.objects.get(
                    user=user,
                    is_deleted=False
                )
                serializer = EmployerProfileSerializer(profile)

            else:
                return Response(
                    {"error": "Profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(serializer.data)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ResumeUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        profile = CandidateProfile.objects.get(
            user=request.user,
            is_deleted=False
        )

        resume = request.FILES.get("resume")

        if not resume:
            return Response(
                {"error": "No resume uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.resume = resume
        profile.save()

        return Response(
            {
                "message": "Resume uploaded successfully.",
                "resume": profile.resume.url
            },
            status=status.HTTP_200_OK
        )
