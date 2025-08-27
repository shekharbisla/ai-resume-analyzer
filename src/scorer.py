# src/scorer.py
from typing import Dict, List, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _extract_keywords(jd_text: str, top_k: int = 20) -> List[str]:
    """
    Very simple keyword getter: take the most frequent non-trivial words
    from the JD. You can replace with RAKE/KeyBERT later.
    """
    words = [w for w in _clean(jd_text).split() if len(w) > 3]
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in ranked[:top_k]]

def similarity_and_gaps(resume_text: str, jd_text: str) -> Dict:
    r = _clean(resume_text)
    j = _clean(jd_text)

    # TF-IDF cosine similarity
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform([j, r])
    sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])

    # Keyword coverage
    kw = _extract_keywords(j)
    present = [k for k in kw if k in r]
    missing = [k for k in kw if k not in r]
    coverage = round(len(present) / max(1, len(kw)) * 100, 1)

    return {
        "similarity": round(sim * 100, 1),
        "coverage": coverage,
        "present_keywords": present,
        "missing_keywords": missing,
    }

def bullet_suggestions(missing: List[str]) -> List[str]:
    bullets = []
    for k in missing[:10]:
        bullets.append(f"Add a bullet showing experience with **{k}** (impact + metric).")
    return bullets
