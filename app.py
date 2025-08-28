# app.py  (root में)
from __future__ import annotations

from datetime import datetime
from typing import List

import streamlit as st

# ---- हमारी src/ helper files से imports (namespace के साथ) ----
from src.parser import read_pdf, read_docx
from src.utils import clean_text, extract_keywords
from src.scorer import score_resume
from src.analyzer import keyword_gaps

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="centered")

# --------------- HELPERS -------------------
def read_any(file) -> str:
    if file is None:
        return ""
    data = file.read()
    name = (file.name or "").lower()
    mime = (file.type or "").lower()

    if "pdf" in mime or name.endswith(".pdf"):
        return read_pdf(data)
    if "word" in mime or name.endswith(".docx"):
        return read_docx(data)
    if "text" in mime or name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")
    raise ValueError("Unsupported file type. Please use PDF, DOCX, or TXT.")

def to_lines(items: List[str]) -> str:
    return "\n".join(f"• {x}" for x in items)

def make_report(resume_text: str, jd_text: str, score: float,
                matched: List[str], missing: List[str],
                suggestions: List[str]) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""AI Resume Analyzer Report
Generated: {ts}

Overall Match Score: {round(score, 1)} / 100

=== Matched Keywords ===
{to_lines(matched) or "—"}

=== Missing / Low-Coverage Keywords ===
{to_lines(missing) or "—"}

=== Suggestions ===
{to_lines(suggestions) or "—"}
"""

# ------------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ How to use")
    st.markdown(
        "1) Upload your **Resume** (PDF/DOCX/TXT)\n"
        "2) Paste or upload the **Job Description**\n"
        "3) Click **Analyze**\n"
        "4) Download the report"
    )
    st.caption("Tip: Tailor each resume to the JD for a higher score.")

# ------------------- MAIN UI ----------------
st.title("🧠 AI Resume Analyzer")
st.caption("Match resume to JD, see keyword gaps, and quick suggestions.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF / DOCX / TXT)",
                                   type=["pdf", "docx", "txt"])
with col2:
    jd_file = st.file_uploader("Optional: Upload JD (PDF / DOCX / TXT)",
                               type=["pdf", "docx", "txt"])

jd_text_input = st.text_area("Or paste Job Description here", height=220)

if st.button("🔍 Analyze", use_container_width=True):
    if not resume_file:
        st.error("Please upload your **Resume** first.")
        st.stop()

    try:
        raw_resume = read_any(resume_file)
    except Exception as e:
        st.error(f"Could not read resume: {e}")
        st.stop()

    raw_jd = ""
    if jd_file:
        try:
            raw_jd = read_any(jd_file)
        except Exception as e:
            st.error(f"Could not read JD: {e}")
            st.stop()
    if not raw_jd:
        raw_jd = jd_text_input

    if not raw_jd.strip():
        st.error("Please add a **Job Description** (upload or paste).")
        st.stop()

    with st.spinner("Analyzing…"):
        resume_text = clean_text(raw_resume)
        jd_text = clean_text(raw_jd)
        jd_keywords = extract_keywords(jd_text, top_n=40)
        matched, missing = keyword_gaps(resume_text, jd_keywords)
        score = score_resume(resume_text, jd_text, matched, missing)

        suggestions: List[str] = []
        if missing:
            suggestions.append(f"Add context for: {', '.join(missing[:10])}")
        if len(matched) < 10:
            suggestions.append("Highlight outcomes with metrics (%, $, time).")
        suggestions.append("Mirror true JD phrases in your bullets.")
        suggestions.append("Surface the most relevant skills near the top.")

    st.success("Analysis complete!")
    st.subheader("Overall Match")
    st.metric("Score", f"{round(score, 1)} / 100")
    st.progress(min(max(score / 100.0, 0.0), 1.0))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ✅ Matched")
        st.write(", ".join(matched) if matched else "—")
    with c2:
        st.markdown("#### ❗ Missing")
        st.write(", ".join(missing) if missing else "—")

    st.markdown("#### 💡 Suggestions")
    for s in suggestions:
        st.write(f"- {s}")

    st.download_button(
        "📄 Download Analysis Report (TXT)",
        data=make_report(resume_text, jd_text, score, matched, missing, suggestions).encode("utf-8"),
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )
