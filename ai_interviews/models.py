from django.db import models

from applications.models import JobApplication


class AICall(models.Model):

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    STATUS_CHOICES = [
        (QUEUED, "Queued"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="ai_call"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=QUEUED
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    error = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"AI Call - Application {self.application.id}"


class AIInterviewSession(models.Model):

    call = models.OneToOneField(
        AICall,
        on_delete=models.CASCADE,
        related_name="session"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True
    )

    transcript = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Interview Session - Call {self.call.id}"


class AIQuestion(models.Model):

    session = models.ForeignKey(
        AIInterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()

    question_order = models.PositiveIntegerField()

    asked_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Question {self.question_order} - Session {self.session.id}"


class AIAnswer(models.Model):

    question = models.OneToOneField(
        AIQuestion,
        on_delete=models.CASCADE,
        related_name="answer"
    )

    answer = models.TextField(
        blank=True
    )

    transcript = models.TextField(
        blank=True
    )

    answered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Answer - Question {self.question.id}"


class CallLog(models.Model):

    call = models.ForeignKey(
        AICall,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    event = models.CharField(
        max_length=100
    )

    message = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.event} - Call {self.call.id}"
