from django.db import models
from profiles.models import CandidateProfile
from jobs.models import Job


class JobApplication(models.Model):

    APPLIED = "APPLIED"
    REVIEWING = "REVIEWING"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"

    STATUS_CHOICES = [
        (APPLIED, "Applied"),
        (REVIEWING, "Reviewing"),
        (SHORTLISTED, "Shortlisted"),
        (REJECTED, "Rejected"),
        (HIRED, "Hired"),
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

    resume = models.FileField(upload_to="applications/")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=APPLIED
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate} -> {self.job}"
