# --- Fix for imports when deploying on Streamlit ---
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# app.py
# AI Resume Analyzer – Streamlit UI
# ---------------------------------
# Upload a resume (PDF/DOCX/TXT) + a Job Description, get:
# - overall match score
# - matched & missing keywords
# - improvement suggestions
# - downloadable analysis report

from __future__ import annotations
import io
import re
from datetime import datetime
from typing import List, Tuple

import streamlit as st

# --- Project imports (our src/ helpers) ---
from src.parser import read_pdf, read_docx
from src.utils import clean_text, extract_keywords
from src.scorer import score_resume
from src.analyzer import keyword_gaps

# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="centered",
)

# --------------- SMALL HELPERS -------------
ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
]

def read_any(file) -> str:
    """Read PDF/DOCX/TXT bytes into text."""
    if file is None:
        return ""
    data = file.read()
    mime = file.type or ""

    if "pdf" in mime:
        return read_pdf(data)
    if "word" in mime or file.name.lower().endswith(".docx"):
        return read_docx(data)
    if "text" in mime or file.name.lower().endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return data.decode("latin-1", errors="ignore")

    # Fallback: try by extension
    if file.name.lower().endswith(".pdf"):
        return read_pdf(data)
    if file.name.lower().endswith(".docx"):
        return read_docx(data)
    if file.name.lower().endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please use PDF, DOCX, or TXT.")

def to_lines(items: List[str]) -> str:
    return "\n".join(f"• {x}" for x in items)

def make_report(
    resume_text: str,
    jd_text: str,
    score: float,
    matched: List[str],
    missing: List[str],
    suggestions: List[str],
) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    report = f"""AI Resume Analyzer Report
Generated: {ts}

Overall Match Score: {round(score, 1)} / 100

=== Matched Keywords ===
{to_lines(matched) or "—"}

=== Missing / Low-Coverage Keywords ===
{to_lines(missing) or "—"}

=== Suggestions ===
{to_lines(suggestions) or "—"}

=== Cleaned Resume Text (preview) ===
{resume_text[:1500]}

=== Cleaned JD Text (preview) ===
{jd_text[:1500]}
"""
    return report

# ------------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ How to use")
    st.markdown(
        "1) Upload your **Resume** (PDF/DOCX/TXT)\n"
        "2) Paste or upload the **Job Description**\n"
        "3) Click **Analyze** to see score & gaps\n"
        "4) Download the report and improve your resume"
    )
    st.divider()
    st.caption("Tip: Use a tailored resume for each JD to improve your score.")

# ------------------- MAIN UI ----------------
st.title("🧠 AI Resume Analyzer")
st.caption("Match your resume to a Job Description, see gaps, and get quick suggestions.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader(
        "Upload Resume (PDF / DOCX / TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
    )
with col2:
    jd_file = st.file_uploader(
        "Optional: Upload JD (PDF / DOCX / TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
    )

jd_text_input = st.text_area(
    "Or paste Job Description here",
    height=220,
    placeholder="Paste the role responsibilities, required skills, tools, and keywords…",
)

analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# ----------------- ANALYZE FLOW -------------
if analyze_btn:
    if not resume_file:
        st.error("Please upload your **Resume** file first.")
        st.stop()

    # Read inputs
    try:
        raw_resume = read_any(resume_file)
    except Exception as e:
        st.error(f"Could not read Resume: {e}")
        st.stop()

    raw_jd = ""
    if jd_file:
        try:
            raw_jd = read_any(jd_file)
        except Exception as e:
            st.error(f"Could not read JD file: {e}")
            st.stop()

    if not raw_jd and not jd_text_input.strip():
        st.error("Please add a **Job Description** (upload file or paste in the box).")
        st.stop()

    if not raw_jd:
        raw_jd = jd_text_input

    with st.spinner("Analyzing…"):
        # Clean text
        resume_text = clean_text(raw_resume)
        jd_text = clean_text(raw_jd)

        # Keywords from JD (top-N)
        jd_keywords = extract_keywords(jd_text, top_n=40)

        # Compute gaps & score
        matched, missing = keyword_gaps(resume_text, jd_keywords)
        score = score_resume(resume_text, jd_text, matched, missing)

        # Suggestions – simple, actionable
        suggestions: List[str] = []
        if missing:
            suggestions.append(
                f"Add context for missing keywords: {', '.join(missing[:10])}"
            )
        if len(matched) < 10:
            suggestions.append("Highlight outcomes with metrics (%, $, time saved).")
        suggestions.append(
            "Mirror key phrases from the JD in your bullet points where true."
        )
        suggestions.append(
            "Place the most relevant skills in the top 1/3 of your resume."
        )

    # --------------- RESULTS UI ---------------
    st.success("Analysis complete!")
    st.subheader("Overall Match")
    st.metric(label="Score", value=f"{round(score, 1)} / 100")

    st.progress(min(max(score / 100.0, 0.0), 1.0))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ✅ Matched Keywords")
        if matched:
            st.write(", ".join(matched))
        else:
            st.write("—")

    with c2:
        st.markdown("#### ❗ Missing / Low-Coverage")
        if missing:
            st.write(", ".join(missing))
        else:
            st.write("—")

    st.markdown("#### 💡 Suggestions")
    for s in suggestions:
        st.write(f"- {s}")

    # Download report
    report_text = make_report(resume_text, jd_text, score, matched, missing, suggestions)
    st.download_button(
        "📄 Download Analysis Report (TXT)",
        data=report_text.encode("utf-8"),
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ----------------- FOOTER -------------------
st.divider()
st.caption(
    "Built with Streamlit. This tool gives guidance only; always tailor your resume truthfully to the role."
)

if __name__ == "__main__":
    # Streamlit runs this file directly; keeping the guard is still good practice.
    pass
