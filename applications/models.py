from django.db import models

from profiles.models import CandidateProfile
from jobs.models import Job


class JobApplication(models.Model):

    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    SELECTED = "SELECTED"

    STATUS_CHOICES = [
        (APPLIED, "Applied"),
        (SHORTLISTED, "Shortlisted"),
        (INTERVIEW, "Interview Scheduled"),
        (REJECTED, "Rejected"),
        (SELECTED, "Selected"),
    ]

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    resume = models.FileField(
        upload_to="applications/"
    )
    ats_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=APPLIED
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"


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
