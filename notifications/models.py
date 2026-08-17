from django.db import models

# Create your models here.


class NotificationLog(models.Model):

    SENT = "SENT"
    FAILED = "FAILED"

    STATUS_CHOICES = [
        (SENT, "Sent"),
        (FAILED, "Failed"),
    ]

    recipient = models.EmailField()

    event = models.CharField(max_length=100)

    subject = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    error = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.recipient} - {self.event} - {self.status}"
