from celery import shared_task

from .automation import auto_process_job_applications


@shared_task
def process_job_applications(job_id):
    return auto_process_job_applications(job_id)
