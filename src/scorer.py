from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _tfidf_sim(a: str, b: str) -> float:
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=1)
    X = vec.fit_transform([a or "", b or ""])
    return float(cosine_similarity(X[0], X[1])[0][0])  # 0..1

def score_resume(resume_text: str, jd_text: str, matched: List[str], missing: List[str]) -> float:
    """Blend of keyword overlap and TF-IDF cosine → return 0..100."""
    total = max(len(matched) + len(missing), 1)
    overlap = len(matched) / total  # 0..1
    sim = _tfidf_sim((resume_text or ""), (jd_text or ""))  # 0..1
    # weights: 60% overlap, 40% semantic sim
    raw = 0.6 * overlap + 0.4 * sim
    return round(max(0.0, min(1.0, raw)) * 100, 1)
