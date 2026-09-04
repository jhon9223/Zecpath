from django.utils import timezone

from ..models import AvailabilitySlot, InterviewSchedule


class SchedulingEngine:

    def get_available_slots(self, job):
        return AvailabilitySlot.objects.filter(
            job=job,
            is_available=True,
            start_time__gte=timezone.now()
        ).order_by("start_time")

    def validate_slot(self, slot):
        if not slot.is_available:
            return False, "Slot is not available."

        if slot.start_time <= timezone.now():
            return False, "Slot must be in the future."

        if slot.end_time <= slot.start_time:
            return False, "Invalid slot time."

        return True, None

    def schedule_interview(self, call, slot):
        is_valid, error = self.validate_slot(slot)

        if not is_valid:
            return None, error

        if InterviewSchedule.objects.filter(
            availability_slot=slot
        ).exists():
            return None, "Slot is already booked."

        schedule = InterviewSchedule.objects.create(
            call=call,
            availability_slot=slot,
            scheduled_start=slot.start_time,
            scheduled_end=slot.end_time,
            status=InterviewSchedule.SCHEDULED,
        )

        slot.is_available = False
        slot.save(update_fields=["is_available"])

        return schedule, None
