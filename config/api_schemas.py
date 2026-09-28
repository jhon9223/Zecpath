
from rest_framework import serializers
from drf_spectacular.utils import OpenApiResponse


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class DashboardStatsSerializer(serializers.Serializer):
    applied_jobs = serializers.IntegerField()
    shortlisted = serializers.IntegerField()
    interviews = serializers.IntegerField()
    selected = serializers.IntegerField()
    rejected = serializers.IntegerField()


class PlatformStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_employers = serializers.IntegerField()
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()


MESSAGE_RESPONSE = OpenApiResponse(
    response=MessageResponseSerializer,
    description="Operation result",
)
