from .tasks import send_notification_email_task


def notify_application_submitted(application):
    candidate = application.candidate.user

    send_notification_email_task.delay(
        recipient=candidate.email,
        event="APPLICATION_SUBMITTED",
        subject="Application Submitted Successfully",
        message=(
            f"Your application for "
            f"{application.job.title} has been submitted successfully."
        )
    )


def notify_application_shortlisted(application):
    candidate = application.candidate.user

    send_notification_email_task.delay(
        recipient=candidate.email,
        event="APPLICATION_SHORTLISTED",
        subject="Application Shortlisted",
        message=(
            f"Congratulations! Your application for "
            f"{application.job.title} has been shortlisted."
        )
    )


def notify_application_rejected(application):
    candidate = application.candidate.user

    send_notification_email_task.delay(
        recipient=candidate.email,
        event="APPLICATION_REJECTED",
        subject="Application Update",
        message=(
            f"Your application for "
            f"{application.job.title} was not selected."
        )
    )
