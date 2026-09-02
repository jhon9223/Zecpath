from ai_interviews.models import JobQuestion


class QuestionEngine:

    def get_questions(self, job):
        return JobQuestion.objects.filter(
            job=job,
            is_active=True,
            question_template__is_active=True,
        ).select_related(
            "question_template"
        ).order_by(
            "question_order"
        )

    def get_next_question(self, job, current_order=0):
        return self.get_questions(job).filter(
            question_order__gt=current_order
        ).first()

    def get_follow_up_question(self, question_template, answer):
        if not question_template.follow_up_question:
            return None

        answer = answer.lower()

        keywords = question_template.follow_up_keywords

        if any(keyword.lower() in answer for keyword in keywords):
            return question_template.follow_up_question

        return None
