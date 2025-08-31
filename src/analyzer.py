from typing import List, Tuple
from src.utils import clean_text

def keyword_gaps(resume_text: str, jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
    """Return (matched, missing) keywords from the JD w.r.t resume."""
    r = clean_text(resume_text).lower()
    matched, missing = [], []
    seen = set()
    for k in jd_keywords:
        if k in seen: 
            continue
        seen.add(k)
        if k.lower() in r:
            matched.append(k)
        else:
            missing.append(k)
    # de-dup while preserving order
    matched = list(dict.fromkeys(matched))
    missing = list(dict.fromkeys(missing))
    # keep lists manageable
    return matched[:50], missing[:50]
