# src/utils.py

import re
from collections import Counter
from nltk.corpus import stopwords
import nltk

# download stopwords first time (safe check)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

STOPWORDS = set(stopwords.words("english"))

# Custom extra stopwords (JD mein unwanted words)
CUSTOM_STOPWORDS = {
    "job", "role", "requirement", "requirements", "looking", "good",
    "great", "skills", "must", "etc", "knowledge", "strong", "excellent",
    "ability", "experience", "applicant", "candidate", "team"
}

# Domain-specific keywords (optional preference)
DOMAIN_KEYWORDS = {
    "python", "java", "c++", "c", "flask", "django",
    "machine", "learning", "deep", "ai", "ml", "sql", "nosql",
    "data", "analysis", "analytics", "numpy", "pandas", "excel", "tableau",
    "power", "bi", "spark", "hadoop", "cloud", "aws", "azure", "gcp",
    "nlp", "transformers", "keras", "pytorch", "tensorflow",
    "communication", "leadership", "management", "developer", "development"
}


def clean_text(text: str) -> str:
    """Basic text cleaning"""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+]", " ", text)  # keep alphanum and +
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(text: str, top_n: int = 30):
    """
    Extract meaningful keywords from text:
    - Removes stopwords
    - Skips very short words
    - Prioritizes domain keywords
    """
    text = clean_text(text)
    words = text.split()

    filtered_words = []
    for w in words:
        if len(w) < 3:  # too short
            continue
        if w in STOPWORDS or w in CUSTOM_STOPWORDS:
            continue
        filtered_words.append(w)

    # count frequency
    word_counts = Counter(filtered_words)

    # sort: domain keywords first, then frequency
    sorted_words = sorted(
        word_counts.keys(),
        key=lambda x: (x not in DOMAIN_KEYWORDS, -word_counts[x])
    )

    return sorted_words[:top_n]
