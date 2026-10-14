from django.db import models
from accounts.models import User
from applications.models import JobApplication


class Conversation(models.Model):
    application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="chat_conversation",
    )

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recruiter_conversations",
    )

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_conversations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat: {self.application}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages",
    )

    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender}"
