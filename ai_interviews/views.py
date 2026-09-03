from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsEmployer
from jobs.models import Job

from .models import AICall, AIAnswer, AIQuestion
from .services.evaluation_service import AnswerEvaluationService
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

        try:
            question = AIQuestion.objects.select_related(
                "session__call__application__job"
            ).get(
                id=question_id
            )
        except AIQuestion.DoesNotExist:
            return Response(
                {
                    "error": "Question not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        answer, created = AIAnswer.objects.update_or_create(
            question=question,
            defaults={
                "answer": answer_text,
                "transcript": answer_text,
            }
        )

        job = question.session.call.application.job

        job_question = get_object_or_404(
            question.session.call.application.job.ai_questions,
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

    def get(self, request, answer_id):

        try:
            answer = AIAnswer.objects.select_related(
                "evaluation"
            ).get(
                id=answer_id
            )
        except AIAnswer.DoesNotExist:
            return Response(
                {
                    "error": "Answer not found."
                },
                status=status.HTTP_404_NOT_FOUND
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
