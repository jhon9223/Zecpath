from datetime import timedelta

from django.utils import timezone

from ..models import InterviewSchedule, ReminderLog, ReminderRule


class ReminderEngine:

    def create_reminders(self, schedule):
        rules = ReminderRule.objects.filter(
            is_active=True
        ).order_by(
            "minutes_before"
        )

        reminders = []

        for rule in rules:
            scheduled_for = (
                schedule.scheduled_start
                - timedelta(minutes=rule.minutes_before)
            )

            reminder, created = ReminderLog.objects.get_or_create(
                schedule=schedule,
                reminder_rule=rule,
                defaults={
                    "scheduled_for": scheduled_for,
                    "status": ReminderLog.PENDING,
                }
            )

            if created:
                reminders.append(reminder)

        return reminders

    def get_due_reminders(self):
        now = timezone.now()

        return ReminderLog.objects.filter(
            status=ReminderLog.PENDING,
            scheduled_for__lte=now,
            schedule__status__in=[
                InterviewSchedule.SCHEDULED,
                InterviewSchedule.CONFIRMED,
            ]
        ).select_related(
            "schedule__call__application__candidate__user",
            "schedule__call__application__job",
            "reminder_rule"
        ).order_by(
            "scheduled_for"
        )
