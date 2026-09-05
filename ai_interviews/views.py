from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsEmployer
from jobs.models import Job
from .tasks import send_interview_confirmation
from .services.reminder_engine import ReminderEngine
from .models import (
    AICall,
    AIAnswer,
    AIQuestion,
    AvailabilitySlot,
    ReminderLog,
)

from .services.evaluation_service import AnswerEvaluationService
from .services.scheduling_engine import SchedulingEngine

from .serializers import (
    AIInterviewSessionSerializer,
    CallLogSerializer,
    AIAnswerEvaluationSerializer,
)


class AIInterviewAuditAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user
        )

        calls = AICall.objects.filter(
            application__job=job
        ).select_related(
            "application__candidate__user"
        ).prefetch_related(
            "session__questions__answer",
            "logs"
        ).order_by(
            "-created_at"
        )

        data = []

        for call in calls:

            session_data = None

            if hasattr(call, "session"):
                session_data = AIInterviewSessionSerializer(
                    call.session
                ).data

            data.append({
                "call_id": call.id,
                "application_id": call.application.id,
                "candidate": call.application.candidate.user.username,
                "status": call.status,
                "scheduled_at": call.scheduled_at,
                "attempts": call.attempts,
                "error": call.error,
                "session": session_data,
                "logs": CallLogSerializer(
                    call.logs.all(),
                    many=True
                ).data,
            })

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "total_calls": calls.count(),
            "queued_calls": calls.filter(
                status=AICall.QUEUED
            ).count(),
            "in_progress_calls": calls.filter(
                status=AICall.IN_PROGRESS
            ).count(),
            "completed_calls": calls.filter(
                status=AICall.COMPLETED
            ).count(),
            "failed_calls": calls.filter(
                status=AICall.FAILED
            ).count(),
            "calls": data,
        })


class AIAnswerEvaluationAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def post(self, request):

        question_id = request.data.get("question_id")
        answer_text = request.data.get("answer")

        if not question_id or not answer_text:
            return Response(
                {
                    "error": "question_id and answer are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        question = get_object_or_404(
            AIQuestion.objects.select_related(
                "session__call__application__job__employer__user"
            ),
            id=question_id,
            session__call__application__job__employer__user=request.user
        )

        job = question.session.call.application.job

        answer, created = AIAnswer.objects.update_or_create(
            question=question,
            defaults={
                "answer": answer_text,
                "transcript": answer_text,
            }
        )

        job_question = get_object_or_404(
            job.ai_questions,
            question_order=question.question_order
        )

        keywords = job_question.question_template.follow_up_keywords

        evaluation_service = AnswerEvaluationService()

        evaluation = evaluation_service.evaluate_answer(
            answer,
            keywords
        )

        serializer = AIAnswerEvaluationSerializer(
            evaluation
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class AIAnswerEvaluationDetailAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, answer_id):

        answer = get_object_or_404(
            AIAnswer.objects.select_related(
                "evaluation",
                "question__session__call__application__job__employer__user"
            ),
            id=answer_id,
            question__session__call__application__job__employer__user=request.user
        )

        if not hasattr(answer, "evaluation"):
            return Response(
                {
                    "error": "Evaluation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AIAnswerEvaluationSerializer(
            answer.evaluation
        )

        return Response(
            serializer.data
        )


class AvailableSlotsAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user
        )

        scheduling_engine = SchedulingEngine()

        slots = scheduling_engine.get_available_slots(job)

        data = [
            {
                "id": slot.id,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
            }
            for slot in slots
        ]

        return Response(data)


class InterviewScheduleAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def post(self, request):

        call_id = request.data.get("call_id")
        slot_id = request.data.get("slot_id")

        if not call_id or not slot_id:
            return Response(
                {
                    "error": "call_id and slot_id are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        call = get_object_or_404(
            AICall.objects.select_related(
                "application__job__employer__user"
            ),
            id=call_id,
            application__job__employer__user=request.user
        )

        if hasattr(call, "schedule"):
            return Response(
                {
                    "error": "This interview is already scheduled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        slot = get_object_or_404(
            AvailabilitySlot,
            id=slot_id,
            job=call.application.job
        )

        scheduling_engine = SchedulingEngine()

        schedule, error = scheduling_engine.schedule_interview(
            call,
            slot
        )

        if error:
            return Response(
                {
                    "error": error
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        reminder_engine = ReminderEngine()
        reminder_engine.create_reminders(schedule)
        send_interview_confirmation.delay(schedule.id)
        return Response(
            {
                "message": "Interview scheduled successfully.",
                "schedule_id": schedule.id,
                "call_id": call.id,
                "slot_id": slot.id,
                "scheduled_start": schedule.scheduled_start,
                "scheduled_end": schedule.scheduled_end,
                "status": schedule.status,
            },
            status=status.HTTP_201_CREATED
        )


class InterviewReminderListAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user
        )

        reminders = ReminderLog.objects.filter(
            schedule__call__application__job=job
        ).select_related(
            "schedule",
            "reminder_rule",
        ).order_by(
            "scheduled_for"
        )

        data = []

        for reminder in reminders:

            data.append({
                "id": reminder.id,
                "schedule_id": reminder.schedule.id,
                "reminder_type": reminder.reminder_rule.reminder_type,
                "reminder_name": reminder.reminder_rule.name,
                "minutes_before": reminder.reminder_rule.minutes_before,
                "scheduled_for": reminder.scheduled_for,
                "status": reminder.status,
                "sent_at": reminder.sent_at,
                "error": reminder.error,
            })

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "total_reminders": reminders.count(),
            "pending_reminders": reminders.filter(
                status=ReminderLog.PENDING
            ).count(),
            "sent_reminders": reminders.filter(
                status=ReminderLog.SENT
            ).count(),
            "failed_reminders": reminders.filter(
                status=ReminderLog.FAILED
            ).count(),
            "reminders": data,
        })
