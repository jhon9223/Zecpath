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
import os

# import the pagination class,and use it in the views where you want to paginate the results.,and set the pagination_class attribute to the ProfilePagination class.
from rest_framework import generics
from .pagination import ProfilePagination
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer
# import the DjangoFilterBackend and the CandidateProfileFilter class, and use them in the CandidateProfileListAPIView to enable filtering of candidate profiles based on the is_deleted field.
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CandidateProfileFilter
from rest_framework.filters import SearchFilter
from .utils import get_user_profile


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

# use the following when you want refactor the code to use the get_user_profile utility function instead of directly querying the CandidateProfile and EmployerProfile models. This will make the code cleaner and more maintainable.
# class MyProfileAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):

#         profile = get_user_profile(request.user)

#         if not profile:
#             return Response(
#                 {"error": "Profile not found"},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         if request.user.role == User.CANDIDATE:
#             serializer = CandidateProfileSerializer(profile)

#         else:
#             serializer = EmployerProfileSerializer(profile)

#         return Response(serializer.data)


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

        profile = get_object_or_404(
            CandidateProfile,
            user=request.user,
            is_deleted=False
        )

        resume = request.FILES.get("resume")

        if not resume:
            return Response(
                {"error": "No resume uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File extension validation
        allowed_extensions = [".pdf", ".doc", ".docx"]

        extension = os.path.splitext(resume.name)[1].lower()

        if extension not in allowed_extensions:
            return Response(
                {"error": "Only PDF, DOC and DOCX files are allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File size validation (2 MB)
        max_size = 2 * 1024 * 1024

        if resume.size > max_size:
            return Response(
                {"error": "Resume size must not exceed 2 MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete old resume if it exists
        if profile.resume:
            profile.resume.delete(save=False)

        # Save new resume
        profile.resume = resume
        profile.save()

        return Response(
            {
                "message": "Resume uploaded successfully.",
                "resume": profile.resume.url if profile.resume else None
            },
            status=status.HTTP_200_OK
        )


class CandidateProfileListAPIView(generics.ListAPIView):

    queryset = CandidateProfile.objects.select_related("user")

    serializer_class = CandidateProfileSerializer

    pagination_class = ProfilePagination

    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_class = CandidateProfileFilter

    search_fields = [
        "user__username",
        "skills",
        "education",
        "experience",
    ]
