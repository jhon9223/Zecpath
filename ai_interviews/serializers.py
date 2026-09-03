from .models import (
    AIInterviewSession,
    AIQuestion,
    AIAnswer,
    CallLog,
    AIAnswerEvaluation
)
from rest_framework import serializers


class AIAnswerEvaluationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIAnswerEvaluation
        fields = [
            "id",
            "answer",
            "relevance_score",
            "completeness_score",
            "keyword_score",
            "final_score",
            "confidence",
            "ai_annotation",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "relevance_score",
            "completeness_score",
            "keyword_score",
            "final_score",
            "confidence",
            "ai_annotation",
            "created_at",
        ]


class AIAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIAnswer
        fields = [
            "id",
            "answer",
            "transcript",
            "answered_at",
        ]


class AIQuestionSerializer(serializers.ModelSerializer):

    answer = AIAnswerSerializer(read_only=True)

    class Meta:
        model = AIQuestion
        fields = [
            "id",
            "question",
            "question_order",
            "asked_at",
            "answer",
        ]


class CallLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallLog
        fields = [
            "id",
            "event",
            "message",
            "created_at",
        ]


class AIInterviewSessionSerializer(serializers.ModelSerializer):

    questions = AIQuestionSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = AIInterviewSession
        fields = [
            "id",
            "started_at",
            "ended_at",
            "transcript",
            "questions",
            "created_at",
            "updated_at",
        ]


class AIAnswerEvaluationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIAnswerEvaluation
        fields = [
            "id",
            "answer",
            "relevance_score",
            "completeness_score",
            "keyword_score",
            "final_score",
            "confidence",
            "ai_annotation",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "relevance_score",
            "completeness_score",
            "keyword_score",
            "final_score",
            "confidence",
            "ai_annotation",
            "created_at",
        ]
