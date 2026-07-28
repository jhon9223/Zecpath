from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.models import User
from .models import CandidateProfile, EmployerProfile
from .serializers import (
    CandidateProfileSerializer,
    EmployerProfileSerializer,
)
from accounts.permissions import IsAdmin
# Create your views here.


class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role == User.CANDIDATE:
            profile = request.user.candidate_profile
            serializer = CandidateProfileSerializer(profile)

        elif request.user.role == User.EMPLOYER:
            profile = request.user.employer_profile
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
            profile = request.user.candidate_profile
            serializer = CandidateProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

        elif request.user.role == User.EMPLOYER:
            profile = request.user.employer_profile
            serializer = EmployerProfileSerializer(
                instance=profile,
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
                serializer = CandidateProfileSerializer(
                    user.candidate_profile
                )

            else:
                serializer = EmployerProfileSerializer(
                    user.employer_profile
                )

            return Response(serializer.data)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
