from utils import clean_text

def keyword_gaps(resume_text: str, jd_keywords: list[str]) -> tuple[list[str], list[str]]:
    """
    Compare JD keywords vs Resume content.
    Returns (matched, missing).
    """
    if not jd_keywords:
        return [], []

    resume_tokens = set(resume_text.split())
    matched = [kw for kw in jd_keywords if kw in resume_tokens]
    missing = [kw for kw in jd_keywords if kw not in resume_tokens]

    return matched, missing

def default_suggestions(matched: list[str], missing: list[str]) -> list[str]:
    """
    Always give suggestions:
    - If keywords missing → show them
    - Otherwise → generic ATS improvement tips
    """
    suggestions = []

    if missing:
        suggestions.append(f"Add these missing keywords: {', '.join(missing[:10])}")

    if len(matched) < 10:
        suggestions.append("Highlight your top 10 skills more clearly.")

    # Always show some universal ATS tips
    suggestions.append("Use measurable outcomes (%, $, numbers) to prove impact.")
    suggestions.append("Keep formatting ATS-friendly (avoid tables, images).")
    suggestions.append("Place the most relevant skills in the first half of your resume.")
    suggestions.append("Tailor your resume for each JD for better chances.")

    return suggestions
