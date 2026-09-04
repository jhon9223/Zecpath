from django.db import models

from applications.models import JobApplication


class AICall(models.Model):

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    STATUS_CHOICES = [
        (QUEUED, "Queued"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="ai_call"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=QUEUED
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    attempts = models.PositiveIntegerField(
        default=0
    )

    error = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"AI Call - Application {self.application.id}"


class AIInterviewSession(models.Model):

    call = models.OneToOneField(
        AICall,
        on_delete=models.CASCADE,
        related_name="session"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True
    )

    transcript = models.JSONField(
        default=list,
        blank=True
    )

    current_question_order = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        default="ACTIVE"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Interview Session - Call {self.call.id}"


class AIQuestion(models.Model):

    session = models.ForeignKey(
        AIInterviewSession,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question = models.TextField()

    question_order = models.PositiveIntegerField()

    asked_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Question {self.question_order} - Session {self.session.id}"


class AIAnswer(models.Model):

    question = models.OneToOneField(
        AIQuestion,
        on_delete=models.CASCADE,
        related_name="answer"
    )

    answer = models.TextField(
        blank=True
    )

    transcript = models.TextField(
        blank=True
    )

    answered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Answer - Question {self.question.id}"


class CallLog(models.Model):

    call = models.ForeignKey(
        AICall,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    event = models.CharField(
        max_length=100
    )

    message = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.event} - Call {self.call.id}"


class QuestionTemplate(models.Model):

    INTRODUCTION = "INTRODUCTION"
    EXPERIENCE = "EXPERIENCE"
    SKILLS = "SKILLS"
    AVAILABILITY = "AVAILABILITY"
    SALARY = "SALARY"

    CATEGORY_CHOICES = [
        (INTRODUCTION, "Introduction"),
        (EXPERIENCE, "Experience"),
        (SKILLS, "Skills"),
        (AVAILABILITY, "Availability"),
        (SALARY, "Salary"),
    ]

    question = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    follow_up_question = models.TextField(
        blank=True,
        null=True
    )

    follow_up_keywords = models.JSONField(
        default=list,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.category} - {self.question[:50]}"


class JobQuestion(models.Model):

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="ai_questions"
    )

    question_template = models.ForeignKey(
        QuestionTemplate,
        on_delete=models.CASCADE,
        related_name="job_questions"
    )

    question_order = models.PositiveIntegerField()

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"Job {self.job.id} - Question {self.question_order}"


class AIAnswerEvaluation(models.Model):
    answer = models.OneToOneField(
        AIAnswer,
        on_delete=models.CASCADE,
        related_name="evaluation"
    )

    relevance_score = models.FloatField(default=0)
    completeness_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)

    final_score = models.FloatField(default=0)

    confidence = models.FloatField(
        null=True,
        blank=True
    )

    ai_annotation = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Evaluation for Answer {self.answer.id}"


class AvailabilitySlot(models.Model):

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="availability_slots"
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.job.title} - {self.start_time}"


class InterviewSchedule(models.Model):

    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    RESCHEDULED = "RESCHEDULED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (SCHEDULED, "Scheduled"),
        (CONFIRMED, "Confirmed"),
        (RESCHEDULED, "Rescheduled"),
        (CANCELLED, "Cancelled"),
        (COMPLETED, "Completed"),
    ]

    call = models.OneToOneField(
        AICall,
        on_delete=models.CASCADE,
        related_name="schedule"
    )

    availability_slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name="schedule"
    )

    scheduled_start = models.DateTimeField()

    scheduled_end = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=SCHEDULED
    )

    confirmation_sent = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Interview Schedule - Call {self.call.id}"
