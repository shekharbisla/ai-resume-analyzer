import re
from collections import Counter

def clean_text(text: str) -> str:
    text = (text or "").replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

STOP = set("""
a an the of and or for with to from by in on at as is are be been being into your you we they it this that those these our i'm we're it's
""".split())

def tokenize_words(text: str):
    text = clean_text(text).lower()
    tokens = re.findall(r"[a-z0-9\+\#\.]{2,}", text)
    return [t for t in tokens if t not in STOP]

def extract_keywords(text: str, top_n: int = 40):
    """Very fast keyword list from JD (no heavy NLP)."""
    toks = tokenize_words(text)
    common = Counter(toks).most_common(top_n * 2)
    # prefer longer/technical-looking tokens
    ranked = [w for (w, c) in common if len(w) >= 3]
    # keep unique order
    seen, out = set(), []
    for w in ranked:
        if w not in seen:
            seen.add(w)
            out.append(w)
        if len(out) >= top_n:
            break
    return out
