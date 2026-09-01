from celery import shared_task

from .models import AICall


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_ai_call(self, call_id):
    call = AICall.objects.get(id=call_id)

    if call.status != AICall.QUEUED:
        return

    call.status = AICall.IN_PROGRESS
    call.attempts += 1
    call.save(update_fields=["status", "attempts", "updated_at"])

    try:
        from .services.voice_service import VoiceService

        phone_number = f"+91{call.application.candidate.user.phone}"

        voice_service = VoiceService()
        sid = voice_service.make_call(phone_number)

        call.status = AICall.COMPLETED
        call.error = None
        call.save(update_fields=["status", "error", "updated_at"])

        return sid

    except Exception as exc:
        call.status = AICall.FAILED
        call.error = str(exc)
        call.save(update_fields=["status", "error", "updated_at"])
        raise
