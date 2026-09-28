
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    inline_serializer,
)

from accounts.permissions import IsEmployer
from jobs.models import Job
from applications.models import JobApplication

from .tasks import send_interview_confirmation
from .services.reminder_engine import ReminderEngine
from .services.evaluation_service import AnswerEvaluationService
from .services.scheduling_engine import SchedulingEngine
from .services.candidate_report_service import CandidateReportService

from .models import (
    AICall,
    AIAnswer,
    AIQuestion,
    AvailabilitySlot,
    ReminderLog,
    AICandidateReport,
)

from .serializers import (
    AIInterviewSessionSerializer,
    CallLogSerializer,
    AIAnswerEvaluationSerializer,
    AICandidateReportSerializer,
)


class AIInterviewAuditAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
    ]

    @extend_schema(
        operation_id="ai_interview_audit_retrieve",
        summary="Retrieve AI interview audit",
        description=(
            "Returns AI interview calls, sessions, and call logs "
            "for a job owned by the authenticated employer."
        ),
        responses={
            200: inline_serializer(
                name="AIInterviewAuditResponse",
                fields={
                    "job_id": serializers.IntegerField(),
                    "job_title": serializers.CharField(),
                    "total_calls": serializers.IntegerField(),
                    "queued_calls": serializers.IntegerField(),
                    "in_progress_calls": serializers.IntegerField(),
                    "completed_calls": serializers.IntegerField(),
                    "failed_calls": serializers.IntegerField(),
                    "calls": serializers.ListField(
                        child=serializers.JSONField()
                    ),
                },
            ),
            404: OpenApiResponse(
                description="Job not found or not owned by this employer."
            ),
        },
    )
    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user,
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
        IsEmployer,
    ]

    @extend_schema(
        operation_id="ai_answer_evaluation_create",
        summary="Evaluate an AI interview answer",
        description=(
            "Creates or updates an answer and evaluates it for a "
            "question belonging to a job owned by the authenticated employer."
        ),
        request=inline_serializer(
            name="AIAnswerEvaluationRequest",
            fields={
                "question_id": serializers.IntegerField(),
                "answer": serializers.CharField(),
            },
        ),
        responses={
            201: AIAnswerEvaluationSerializer,
            400: OpenApiResponse(
                description="question_id and answer are required."
            ),
            404: OpenApiResponse(
                description="Question not found or not accessible."
            ),
        },
    )
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
            session__call__application__job__employer__user=request.user,
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
            question_order=question.question_order,
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
        IsEmployer,
    ]

    @extend_schema(
        operation_id="ai_answer_evaluation_detail_retrieve",
        summary="Retrieve answer evaluation",
        description=(
            "Returns an evaluation for an answer belonging to a job "
            "owned by the authenticated employer."
        ),
        responses={
            200: AIAnswerEvaluationSerializer,
            404: OpenApiResponse(
                description="Answer or evaluation not found."
            ),
        },
    )
    def get(self, request, answer_id):

        answer = get_object_or_404(
            AIAnswer.objects.select_related(
                "evaluation",
                "question__session__call__application__job__employer__user"
            ),
            id=answer_id,
            question__session__call__application__job__employer__user=request.user,
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
        IsEmployer,
    ]

    @extend_schema(
        operation_id="interview_available_slots_list",
        summary="List available interview slots",
        description=(
            "Returns available scheduling slots for a job owned "
            "by the authenticated employer."
        ),
        responses={
            200: inline_serializer(
                name="AvailableInterviewSlotResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "start_time": serializers.DateTimeField(),
                    "end_time": serializers.DateTimeField(),
                },
                many=True,
            ),
            404: OpenApiResponse(
                description="Job not found or not owned by this employer."
            ),
        },
    )
    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user,
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
        IsEmployer,
    ]

    @extend_schema(
        operation_id="interview_schedule_create",
        summary="Schedule an interview",
        description=(
            "Schedules an interview using an available slot "
            "for a job owned by the authenticated employer."
        ),
        request=inline_serializer(
            name="InterviewScheduleRequest",
            fields={
                "call_id": serializers.IntegerField(),
                "slot_id": serializers.IntegerField(),
            },
        ),
        responses={
            201: inline_serializer(
                name="InterviewScheduleResponse",
                fields={
                    "message": serializers.CharField(),
                    "schedule_id": serializers.IntegerField(),
                    "call_id": serializers.IntegerField(),
                    "slot_id": serializers.IntegerField(),
                    "scheduled_start": serializers.DateTimeField(),
                    "scheduled_end": serializers.DateTimeField(),
                    "status": serializers.CharField(),
                },
            ),
            400: OpenApiResponse(
                description="Missing fields, duplicate schedule, or scheduling error."
            ),
            404: OpenApiResponse(
                description="Interview call or availability slot not found."
            ),
        },
    )
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
            application__job__employer__user=request.user,
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
            job=call.application.job,
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
        IsEmployer,
    ]

    @extend_schema(
        operation_id="interview_reminders_list",
        summary="List interview reminders",
        description=(
            "Returns reminder records for interviews associated "
            "with a job owned by the authenticated employer."
        ),
        responses={
            200: inline_serializer(
                name="InterviewReminderListResponse",
                fields={
                    "job_id": serializers.IntegerField(),
                    "job_title": serializers.CharField(),
                    "total_reminders": serializers.IntegerField(),
                    "pending_reminders": serializers.IntegerField(),
                    "sent_reminders": serializers.IntegerField(),
                    "failed_reminders": serializers.IntegerField(),
                    "reminders": serializers.ListField(
                        child=serializers.JSONField()
                    ),
                },
            ),
            404: OpenApiResponse(
                description="Job not found or not owned by this employer."
            ),
        },
    )
    def get(self, request, job_id):

        job = get_object_or_404(
            Job,
            id=job_id,
            employer__user=request.user,
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


class AICandidateReportAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer,
    ]

    @extend_schema(
        operation_id="ai_candidate_report_create",
        summary="Generate candidate report",
        description=(
            "Generates an AI candidate report for an application "
            "belonging to a job owned by the authenticated employer."
        ),
        request=None,
        responses={
            200: AICandidateReportSerializer,
            404: OpenApiResponse(
                description="Application not found or not owned by this employer."
            ),
        },
    )
    def post(self, request, application_id):

        application = get_object_or_404(
            JobApplication.objects.select_related(
                "job__employer__user"
            ),
            id=application_id,
            job__employer__user=request.user,
        )

        service = CandidateReportService()
        report = service.generate_report(application)

        serializer = AICandidateReportSerializer(report)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="ai_candidate_report_retrieve",
        summary="Retrieve candidate report",
        description=(
            "Returns the existing AI candidate report for an application "
            "belonging to a job owned by the authenticated employer."
        ),
        responses={
            200: AICandidateReportSerializer,
            404: OpenApiResponse(
                description="Application or candidate report not found."
            ),
        },
    )
    def get(self, request, application_id):

        application = get_object_or_404(
            JobApplication,
            id=application_id,
            job__employer__user=request.user,
        )

        report = get_object_or_404(
            AICandidateReport,
            application=application,
        )

        serializer = AICandidateReportSerializer(report)

        return Response(serializer.data)
