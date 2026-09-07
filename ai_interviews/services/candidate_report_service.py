import json

from ..models import (
    AICandidateReport,
    AIAnswerEvaluation,
)
from .llm_service import LLMService


class CandidateReportService:

    def __init__(self):
        self.llm_service = LLMService()

    def generate_report(self, application):

        evaluations = AIAnswerEvaluation.objects.filter(
            answer__question__session__call__application=application
        ).select_related(
            "answer__question"
        )

        if evaluations.exists():
            ai_call_score = round(
                sum(e.final_score for e in evaluations)
                / evaluations.count(),
                2
            )
        else:
            ai_call_score = 0

        ats_score = float(getattr(application, "ats_score", 0) or 0)
        overall_score = round(
            (ats_score + ai_call_score) / 2,
            2
        )

        interview_data = []

        for evaluation in evaluations:
            interview_data.append({
                "question": evaluation.answer.question.question,
                "answer": evaluation.answer.answer,
                "relevance_score": evaluation.relevance_score,
                "completeness_score": evaluation.completeness_score,
                "keyword_score": evaluation.keyword_score,
                "final_score": evaluation.final_score,
                "annotation": evaluation.ai_annotation,
            })

        prompt = f"""
You are an AI recruitment assistant.

Generate a recruiter-friendly candidate evaluation.

ATS Score: {ats_score}
AI Interview Score: {ai_call_score}
Overall Score: {overall_score}

Interview evaluation data:
{json.dumps(interview_data, default=str)}

Return ONLY valid JSON in this exact structure:

{{
    "summary": "short recruiter-friendly summary",
    "strengths": [
        "strength 1",
        "strength 2"
    ],
    "risks": [
        "risk 1",
        "risk 2"
    ]
}}

Do not include markdown or code fences.
"""

        ai_result = self.llm_service.generate_response(prompt)

        try:
            report_data = json.loads(ai_result)
        except json.JSONDecodeError:
            report_data = {
                "summary": ai_result,
                "strengths": [],
                "risks": [],
            }

        report, created = AICandidateReport.objects.update_or_create(
            application=application,
            defaults={
                "ats_score": ats_score,
                "ai_call_score": ai_call_score,
                "overall_score": overall_score,
                "summary": report_data.get("summary", ""),
                "strengths": report_data.get("strengths", []),
                "risks": report_data.get("risks", []),
            },
        )

        return report
