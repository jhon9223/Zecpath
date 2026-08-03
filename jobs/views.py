from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsEmployer
from rest_framework.permissions import IsAuthenticated

from .models import Job
from .serializers import JobSerializer

from profiles.models import EmployerProfile
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
