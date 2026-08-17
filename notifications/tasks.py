from celery import shared_task

from .services import send_notification_email


@shared_task(
    bind=True,
    # If the email sending raises an exception, Celery can retry the task.
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def send_notification_email_task(
    self,
    recipient,
    event,
    subject,
    message
):
    return send_notification_email(
        recipient=recipient,
        event=event,
        subject=subject,
        message=message
    )
