def score_resume(resume_text: str, jd_text: str, matched: list[str], missing: list[str]) -> float:
    """
    Stable scoring:
    Score = % coverage of JD keywords in Resume.
    Always between 0 and 100.
    """
    total_keywords = len(matched) + len(missing)
    if total_keywords == 0:
        return 0.0

    # Percentage coverage
    coverage = len(matched) / total_keywords

    # More realistic scoring: small bonus if resume has >20 keywords
    length_bonus = 0.05 if len(resume_text.split()) > 20 else 0.0

    score = (coverage + length_bonus) * 100

    return round(min(score, 100.0), 1)
