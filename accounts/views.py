from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignupSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import LogoutSerializer
from .serializers import ProfileSerializer
from .permissions import (
    IsAdmin,
    IsEmployer,
    IsCandidate,
)
# Create your views here.


class SignupAPIView(APIView):

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
    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):
        return Response({"message": "Welcome Candidate"})


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": "Welcome Admin"})
