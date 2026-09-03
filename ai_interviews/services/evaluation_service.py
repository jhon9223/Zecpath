import json

from ..models import AIAnswerEvaluation
from .scoring_engine import ScoringEngine
from .llm_service import LLMService


class AnswerEvaluationService:

    def __init__(self):
        self.llm_service = LLMService()
        self.scoring_engine = ScoringEngine()

    def evaluate_answer(self, answer, keywords=None):
        keywords = keywords or []

        prompt = f"""
Evaluate the following interview answer.

Question:
{answer.question.question}

Candidate Answer:
{answer.answer}

Return ONLY valid JSON in this exact format:

{{
    "relevance_score": 0,
    "completeness_score": 0,
    "confidence": 0,
    "ai_annotation": ""
}}

Rules:
- relevance_score: 0 to 100
- completeness_score: 0 to 100
- confidence: 0 to 100
- ai_annotation: short explanation
"""

        response = self.llm_service.generate_response(prompt)

        try:
            result = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            result = {
                "relevance_score": 0,
                "completeness_score": 0,
                "confidence": 0,
                "ai_annotation": "Unable to parse AI evaluation."
            }

        keyword_score = self.scoring_engine.calculate_keyword_score(
            answer.answer,
            keywords
        )

        final_score = self.scoring_engine.calculate_final_score(
            result["relevance_score"],
            result["completeness_score"],
            keyword_score
        )

        evaluation, created = AIAnswerEvaluation.objects.update_or_create(
            answer=answer,
            defaults={
                "relevance_score": result["relevance_score"],
                "completeness_score": result["completeness_score"],
                "keyword_score": keyword_score,
                "final_score": final_score,
                "confidence": result["confidence"],
                "ai_annotation": result["ai_annotation"],
            }
        )

        return evaluation
