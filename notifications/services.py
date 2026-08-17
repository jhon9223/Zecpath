from django.core.mail import send_mail

from .models import NotificationLog


def send_notification_email(
    recipient,
    event,
    subject,
    message
):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email="noreply@zecpath.com",
            recipient_list=[recipient],
            fail_silently=False
        )

        NotificationLog.objects.create(
            recipient=recipient,
            event=event,
            subject=subject,
            status=NotificationLog.SENT
        )

        return True

    except Exception as e:  # Catch the exception and store it in the variable e.

        NotificationLog.objects.create(
            recipient=recipient,
            event=event,
            subject=subject,
            status=NotificationLog.FAILED,
            error=str(e)
        )

        return False
