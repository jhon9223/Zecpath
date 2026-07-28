from rest_framework import serializers
from .models import CandidateProfile, EmployerProfile


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = "__all__"
        read_only_fields = ("user",)


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = "__all__"
        read_only_fields = ("user",)
