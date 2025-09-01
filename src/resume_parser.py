# src/resume_parser.py

import re
from typing import Dict, List

def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text (basic keyword matching)"""
    skill_keywords = [
        "python", "java", "c++", "c", "flask", "django", "sql", "nosql",
        "pandas", "numpy", "excel", "tableau", "power bi", "spark", "hadoop",
        "machine learning", "deep learning", "ai", "nlp", "pytorch",
        "tensorflow", "keras", "communication", "leadership", "teamwork"
    ]
    found = []
    for kw in skill_keywords:
        if re.search(rf"\b{kw}\b", text.lower()):
            found.append(kw.title())
    return list(set(found))  # unique skills

def extract_experience(text: str) -> List[str]:
    """Extract experience lines (looking for years, months, roles)"""
    lines = text.split("\n")
    exp = []
    for line in lines:
        if re.search(r"(intern|developer|engineer|manager|years?|months?)", line.lower()):
            exp.append(line.strip())
    return exp

def extract_education(text: str) -> List[str]:
    """Extract education details"""
    edu_keywords = ["b.tech", "m.tech", "bsc", "msc", "bca", "mca", "mba", "university", "college", "school"]
    lines = text.split("\n")
    edu = []
    for line in lines:
        if any(kw in line.lower() for kw in edu_keywords):
            edu.append(line.strip())
    return edu

def extract_certifications(text: str) -> List[str]:
    """Extract certifications"""
    lines = text.split("\n")
    certs = []
    for line in lines:
        if "certified" in line.lower() or "certification" in line.lower() or "coursera" in line.lower():
            certs.append(line.strip())
    return certs

def parse_resume(text: str) -> Dict:
    """Main function to parse resume into structured JSON"""
    return {
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
    }
