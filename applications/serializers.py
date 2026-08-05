from rest_framework import serializers
from .models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = (
            "candidate",
            "job",
            "status",
            "applied_at",
        )
