from .models import JobApplication
from .services import update_application_status
SHORTLIST_THRESHOLD = 70
REJECT_THRESHOLD = 40


def determine_application_status(ats_score):
    if ats_score is None:
        return None

    if ats_score >= SHORTLIST_THRESHOLD:
        return "SHORTLISTED"

    if ats_score < REJECT_THRESHOLD:
        return "REJECTED"

    return "APPLIED"


def auto_process_application(application):
    status = determine_application_status(
        application.ats_score
    )

    if status is None:
        return application

    update_application_status(
        application,
        status
    )

    return application


def auto_process_job_applications(job_id):
    applications = JobApplication.objects.filter(
        job_id=job_id,
        ats_score__isnull=False,
        status=JobApplication.APPLIED
    )

    processed = 0

    for application in applications:
        auto_process_application(application)
        processed += 1

    return processed
