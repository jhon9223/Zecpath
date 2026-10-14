from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(
        source="sender.email",
        read_only=True,
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_email",
            "content",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "conversation",
            "sender",
            "sender_email",
            "is_read",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "application",
            "recruiter",
            "candidate",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
