# src/analyzer.py
from typing import Dict, List
import math
from .utils import clean_text, extract_skills

def keyword_coverage(resume: str, jd: str) -> Dict:
    """Simple keyword coverage calc between resume and job description."""
    resume_l = clean_text(resume).lower()
    jd_l = clean_text(jd).lower()
    jd_words = {w for w in jd_l.split() if len(w) > 3}
    found = sorted({w for w in jd_words if w in resume_l})
    missing = sorted(list(jd_words - set(found)))[:50]
    score = round(100 * len(found) / max(len(jd_words), 1), 1)
    return {"score": score, "found": found, "missing": missing}

def analyze(resume_text: str, job_desc: str) -> Dict:
    resume_text = clean_text(resume_text)
    job_desc = clean_text(job_desc)

    # skill extraction
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_desc)

    common = sorted(set(resume_skills) & set(jd_skills))
    missing_skills = sorted(set(jd_skills) - set(resume_skills))

    # keyword coverage
    coverage = keyword_coverage(resume_text, job_desc)

    # quick ATS tips (rule-based)
    tips: List[str] = []
    if len(resume_text) < 800:
        tips.append("Resume bahut short lag raha hai—projects / impact bullets add karo.")
    if "@" not in resume_text:
        tips.append("Contact email clearly add karo.")
    if not common:
        tips.append("JD se matching skill keywords resume me add karo (same wording).")

    return {
        "skills_in_resume": resume_skills,
        "skills_in_jd": jd_skills,
        "skills_overlap": common,
        "skills_missing": missing_skills,
        "coverage": coverage,
        "tips": tips
    }
