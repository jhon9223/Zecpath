from django.utils import timezone

from ..models import (
    AIInterviewSession,
    AIQuestion,
    AIAnswer,
    JobQuestion,
)
from .question_engine import QuestionEngine


class InterviewFlowManager:

    def __init__(self):
        self.question_engine = QuestionEngine()

    def start_interview(self, call):
        session, created = AIInterviewSession.objects.get_or_create(
            call=call
        )

        if created:
            session.started_at = timezone.now()
            session.current_question_order = 0
            session.status = "ACTIVE"

            session.save(
                update_fields=[
                    "started_at",
                    "current_question_order",
                    "status",
                ]
            )

        return session

    def get_next_question(self, session):
        job = session.call.application.job

        next_job_question = self.question_engine.get_next_question(
            job,
            session.current_question_order
        )

        if not next_job_question:
            session.status = "COMPLETED"
            session.ended_at = timezone.now()

            session.save(
                update_fields=[
                    "status",
                    "ended_at",
                ]
            )

            return None

        question = AIQuestion.objects.create(
            session=session,
            question=next_job_question.question_template.question,
            question_order=next_job_question.question_order,
            asked_at=timezone.now(),
        )

        session.current_question_order = (
            next_job_question.question_order
        )

        session.save(
            update_fields=[
                "current_question_order"
            ]
        )

        return question

    def save_answer(self, question, answer_text):
        answer, created = AIAnswer.objects.update_or_create(
            question=question,
            defaults={
                "answer": answer_text,
                "transcript": answer_text,
                "answered_at": timezone.now(),
            }
        )

        return answer

    def get_next_step(self, question, answer_text):
        job_question = JobQuestion.objects.get(
            job=question.session.call.application.job,
            question_order=question.question_order
        )

        follow_up = self.question_engine.get_follow_up_question(
            job_question.question_template,
            answer_text
        )

        if follow_up:
            return AIQuestion.objects.create(
                session=question.session,
                question=follow_up,
                question_order=question.question_order,
                asked_at=timezone.now(),
            )

        return self.get_next_question(question.session)
