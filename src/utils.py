import re

# --- Clean text (basic preprocessing) ---
def clean_text(text: str) -> str:
    """Lowercase + remove non-alphabets + normalize spaces."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# --- Deterministic keyword extraction ---
def extract_keywords(text: str, top_n: int = 40) -> list[str]:
    """
    Extract keywords in a stable way:
    - Split by spaces
    - Remove short/common words
    - Return top unique tokens (deterministic order)
    """
    text = clean_text(text)
    tokens = text.split()

    # simple stopwords list
    stopwords = {"the", "and", "or", "a", "an", "in", "on", "for", "to", "with", "of"}

    # filter tokens
    keywords = [t for t in tokens if len(t) > 2 and t not in stopwords]

    # unique + deterministic
    keywords = sorted(set(keywords))

    return keywords[:top_n]
