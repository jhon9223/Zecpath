import pdfplumber
from docx import Document


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
