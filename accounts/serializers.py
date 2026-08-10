from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import *


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "role",

        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        refresh_token = self.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "is_verified",
            "created_at",
        ]


class AdminActionLogSerializer(serializers.ModelSerializer):

    admin_username = serializers.CharField(
        source="admin.username",
        read_only=True
    )

    target_username = serializers.CharField(
        source="target_user.username",
        read_only=True
    )

    class Meta:
        model = AdminActionLog
        fields = [
            "id",
            "admin_username",
            "action",
            "target_username",
            "created_at"
        ]
