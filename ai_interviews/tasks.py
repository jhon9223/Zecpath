from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import AICall, InterviewSchedule, ReminderLog
from .services.reminder_engine import ReminderEngine


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def process_ai_call(self, call_id):

    call = AICall.objects.get(id=call_id)

    if call.status != AICall.QUEUED:
        return

    call.status = AICall.IN_PROGRESS
    call.attempts += 1

    call.save(
        update_fields=[
            "status",
            "attempts",
            "updated_at"
        ]
    )

    try:
        from .services.voice_service import VoiceService

        phone_number = f"+91{call.application.candidate.user.phone}"

        voice_service = VoiceService()

        sid = voice_service.make_call(phone_number)

        call.status = AICall.COMPLETED
        call.error = None

        call.save(
            update_fields=[
                "status",
                "error",
                "updated_at"
            ]
        )

        return sid

    except Exception as exc:

        call.status = AICall.FAILED
        call.error = str(exc)

        call.save(
            update_fields=[
                "status",
                "error",
                "updated_at"
            ]
        )

        raise


@shared_task
def send_interview_confirmation(schedule_id):

    try:
        schedule = InterviewSchedule.objects.select_related(
            "call__application__candidate__user",
            "call__application__job"
        ).get(id=schedule_id)

    except InterviewSchedule.DoesNotExist:
        return

    user = schedule.call.application.candidate.user
    job = schedule.call.application.job

    if not user.email:
        return

    send_mail(
        subject="AI Interview Scheduled",
        message=(
            f"Your AI interview for the position "
            f"'{job.title}' has been scheduled.\n\n"
            f"Date and Time: {schedule.scheduled_start}\n"
            f"End Time: {schedule.scheduled_end}\n\n"
            f"Please be available at the scheduled time."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    schedule.confirmation_sent = True
    schedule.status = InterviewSchedule.CONFIRMED

    schedule.save(
        update_fields=[
            "confirmation_sent",
            "status"
        ]
    )


@shared_task(bind=True, max_retries=3)
def send_interview_reminder(self, reminder_id):

    try:
        reminder = ReminderLog.objects.select_related(
            "schedule__call__application__candidate__user",
            "schedule__call__application__job",
            "reminder_rule",
        ).get(id=reminder_id)

    except ReminderLog.DoesNotExist:
        return

    if reminder.status != ReminderLog.PENDING:
        return

    user = reminder.schedule.call.application.candidate.user
    job = reminder.schedule.call.application.job

    if not user.email:
        reminder.status = ReminderLog.FAILED
        reminder.error = "Candidate email not available."

        reminder.save(
            update_fields=[
                "status",
                "error"
            ]
        )

        return

    try:
        send_mail(
            subject=f"AI Interview Reminder - {job.title}",
            message=(
                f"This is a reminder for your AI interview for the position "
                f"'{job.title}'.\n\n"
                f"Date and Time: {reminder.schedule.scheduled_start}\n"
                f"End Time: {reminder.schedule.scheduled_end}\n\n"
                f"Please be available at the scheduled time."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        reminder.status = ReminderLog.SENT
        reminder.sent_at = timezone.now()
        reminder.error = ""

        reminder.save(
            update_fields=[
                "status",
                "sent_at",
                "error"
            ]
        )

    except Exception as exc:

        reminder.error = str(exc)

        if self.request.retries >= self.max_retries:
            reminder.status = ReminderLog.FAILED

            reminder.save(
                update_fields=[
                    "status",
                    "error"
                ]
            )

            return

        reminder.save(
            update_fields=[
                "error"
            ]
        )

        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )


@shared_task
def scan_due_reminders():

    reminder_engine = ReminderEngine()

    reminders = reminder_engine.get_due_reminders()

    for reminder in reminders:
        send_interview_reminder.delay(reminder.id)
