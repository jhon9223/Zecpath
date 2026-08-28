from datetime import time, timedelta

from django.utils import timezone

from jobs.models import Job

from .models import JobApplication, AICall


CALL_START = time(8, 0)
CALL_END = time(20, 0)


def is_calling_window():
    current_time = timezone.localtime().time()

    return CALL_START <= current_time <= CALL_END


def get_next_calling_time():
    now = timezone.localtime()

    if now.time() < CALL_START:
        return now.replace(
            hour=CALL_START.hour,
            minute=CALL_START.minute,
            second=0,
            microsecond=0
        )

    next_day = now + timedelta(days=1)

    return next_day.replace(
        hour=CALL_START.hour,
        minute=CALL_START.minute,
        second=0,
        microsecond=0
    )


def should_create_ai_call(application):

    if application.status != JobApplication.SHORTLISTED:
        return False

    if application.job.status != Job.ACTIVE:
        return False

    return True


def create_ai_call(application):

    if not should_create_ai_call(application):
        return None

    if AICall.objects.filter(application=application).exists():
        return None

    if is_calling_window():
        scheduled_at = timezone.now()
    else:
        scheduled_at = get_next_calling_time()

    return AICall.objects.create(
        application=application,
        status=AICall.QUEUED,
        scheduled_at=scheduled_at
    )
