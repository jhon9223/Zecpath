import pdfplumber
from docx import Document
import re

from .skills import SKILLS


def extract_text_from_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_text_from_docx(file):
    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_resume_text(file):

    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)

    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)

    else:
        raise ValueError("Unsupported file format.")


def clean_resume_text(text):
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def extract_skills(text):
    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def extract_experience(text):
    pattern = r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)"

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    return matches


ROLES = [
    "Python Developer",
    "Python Backend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Developer",
    "Software Engineer",
    "Frontend Developer",
    "Web Developer",
    "Data Scientist",
    "Machine Learning Engineer",
]


def extract_roles(text):
    found_roles = []

    for role in ROLES:
        pattern = r"\b" + re.escape(role) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_roles.append(role)

    return found_roles


EDUCATION = [
    "BCA",
    "Bachelor of Computer Applications",
    "B.Tech",
    "Bachelor of Technology",
    "MCA",
    "Master of Computer Applications",
    "M.Tech",
    "MBA",
    "Bachelor of Science",
    "Master of Science",
]


def extract_education(text):
    found_education = []

    for education in EDUCATION:
        pattern = r"\b" + re.escape(education) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_education.append(education)

    return found_education


def parse_resume(text):
    return {
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "roles": extract_roles(text),
        "education": extract_education(text),
    }
