# src/parser_v2.py
from io import BytesIO
import PyPDF2
from docx import Document
import re
import json

# Pre-defined skill keywords (Phase 1 simple version)
SKILL_KEYWORDS = [
    "Python", "Java", "C++", "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Data Science", "Excel", "SQL",
    "Pandas", "NumPy", "Power BI", "Tableau", "Communication",
    "Teamwork", "Leadership", "Project Management", "AWS", "Docker"
]

def read_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)

def extract_resume_data(file_bytes: bytes, file_type: str) -> dict:
    """Extract skills + experience from resume"""
    text = ""
    if file_type.endswith(".pdf"):
        text = read_pdf(file_bytes)
    elif file_type.endswith(".docx"):
        text = read_docx(file_bytes)
    else:
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except:
            text = file_bytes.decode("latin-1", errors="ignore")

    # Normalize text
    text_lower = text.lower()

    # Extract skills (simple keyword match)
    found_skills = [skill for skill in SKILL_KEYWORDS if skill.lower() in text_lower]

    # Extract years of experience (basic regex)
    exp_match = re.findall(r"(\d+)\s+year", text_lower)
    experience = f"{max(map(int, exp_match))} years" if exp_match else "Not specified"

    data = {
        "skills": found_skills,
        "experience": experience,
        "raw_text_sample": text[:300]  # preview
    }
    return data

# Debug run
if __name__ == "__main__":
    with open("resume.txt", "rb") as f:
        resume_data = extract_resume_data(f.read(), "resume.txt")
        print(json.dumps(resume_data, indent=2))
