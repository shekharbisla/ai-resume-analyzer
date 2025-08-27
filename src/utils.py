# src/utils.py
import re

COMMON_SKILLS = {
    "python", "sql", "excel", "power bi", "tableau", "numpy", "pandas",
    "scikit-learn", "machine learning", "deep learning", "nlp",
    "communication", "problem solving", "git", "fastapi", "django"
}

def clean_text(text: str) -> str:
    # collapse whitespace and lowercase
    text = re.sub(r"\s+", " ", text or " ").strip()
    return text

def tokenize(text: str):
    text = clean_text(text).lower()
    # split on non-letters/numbers
    return re.findall(r"[a-zA-Z0-9\+\#\.]+", text)

def extract_skills(text: str):
    tokens = " ".join(tokenize(text))
    found = sorted({s for s in COMMON_SKILLS if s in tokens})
    return found
