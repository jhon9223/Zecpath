from .models import JobApplication

from notifications.events import (
    notify_application_shortlisted,
    notify_application_rejected,
)

from resumes.services import (
    extract_resume_text,
    clean_resume_text,
    parse_resume,
)

from .call_service import create_ai_call


SKILL_WEIGHT = 60
EXPERIENCE_WEIGHT = 25
EDUCATION_WEIGHT = 15


def calculate_skill_score(job_skills, resume_skills):
    job_skills = {
        skill.strip().lower()
        for skill in job_skills.split(",")
        if skill.strip()
    }

    resume_skills = {
        skill.strip().lower()
        for skill in resume_skills
    }

    if not job_skills:
        return 0

    matched_skills = job_skills.intersection(resume_skills)

    return (
        len(matched_skills) / len(job_skills)
    ) * SKILL_WEIGHT


def calculate_experience_score(job_experience, resume_experience):

    try:
        job_years = float(job_experience)
    except (ValueError, TypeError):
        return 0

    if not resume_experience:
        return 0

    try:
        candidate_years = max(
            float(year)
            for year in resume_experience
        )
    except (ValueError, TypeError):
        return 0

    if candidate_years >= job_years:
        return EXPERIENCE_WEIGHT

    return (
        candidate_years / job_years
    ) * EXPERIENCE_WEIGHT


def calculate_education_score(job_education, resume_education):
    if not job_education:
        return EDUCATION_WEIGHT

    if not resume_education:
        return 0

    job_education = job_education.lower()

    for education in resume_education:
        if education.lower() in job_education:
            return EDUCATION_WEIGHT

    return 0


def calculate_ats_score(
    skill_score,
    experience_score,
    education_score
):
    total_score = (
        skill_score
        + experience_score
        + education_score
    )

    return round(total_score, 2)


def calculate_application_ats_score(application):
    # 1. Read the resume submitted with this application
    resume_file = application.resume

    # 2. Extract resume text
    text = extract_resume_text(resume_file)

    # 3. Clean the text
    cleaned_text = clean_resume_text(text)

    # 4. Parse resume into structured data
    resume_data = parse_resume(cleaned_text)

    # 5. Calculate individual scores
    skill_score = calculate_skill_score(
        application.job.skills,
        resume_data["skills"]
    )

    experience_score = calculate_experience_score(
        application.job.experience,
        resume_data["experience"]
    )

    education_score = calculate_education_score(
        application.job.education,
        resume_data["education"]
    )

    # 6. Calculate final score
    total_score = calculate_ats_score(
        skill_score,
        experience_score,
        education_score
    )

    return {
        "score": total_score,
        "skills_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "resume_data": resume_data,
    }


def update_application_status(application, new_status):

    old_status = application.status

    application.status = new_status

    application.save(
        update_fields=["status"]
    )

    if (
        new_status == JobApplication.SHORTLISTED
        and old_status != JobApplication.SHORTLISTED
    ):
        notify_application_shortlisted(application)

        create_ai_call(application)

    elif (
        new_status == JobApplication.REJECTED
        and old_status != JobApplication.REJECTED
    ):
        notify_application_rejected(application)

    return application
