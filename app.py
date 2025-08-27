# app.py
# AI Resume Analyzer – Streamlit UI

from __future__ import annotations  # <- Yeh sabse pehle hi hoga

# --- Fix for imports when deploying on Streamlit ---
import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- Standard Libraries ---
from datetime import datetime
from typing import List
import streamlit as st

# --- Project Imports (direct from src folder) ---
from parser import read_pdf, read_docx
from utils import clean_text, extract_keywords
from scorer import score_resume
from analyzer import keyword_gaps


# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="centered",
)

ALLOWED_TYPES = ["pdf", "docx", "txt"]


def read_any(file) -> str:
    """Read PDF/DOCX/TXT bytes into text."""
    if file is None:
        return ""
    data = file.read()
    fname = file.name.lower()

    if fname.endswith(".pdf"):
        return read_pdf(data)
    if fname.endswith(".docx"):
        return read_docx(data)
    if fname.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please use PDF, DOCX, or TXT.")


def to_lines(items: List[str]) -> str:
    return "\n".join(f"• {x}" for x in items)


def make_report(resume_text, jd_text, score, matched, missing, suggestions) -> str:
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

=== Resume Preview ===
{resume_text[:1000]}

=== JD Preview ===
{jd_text[:1000]}
"""
    return report


# ------------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ How to use")
    st.markdown(
        "1) Upload your **Resume** (PDF/DOCX/TXT)\n"
        "2) Upload or paste the **Job Description**\n"
        "3) Click **Analyze**\n"
        "4) Download your report"
    )


# ------------------- MAIN UI ----------------
st.title("🧠 AI Resume Analyzer")
st.caption("Match your resume to a Job Description, see keyword gaps, and get quick suggestions.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=ALLOWED_TYPES)
with col2:
    jd_file = st.file_uploader("Upload Job Description (optional)", type=ALLOWED_TYPES)

jd_text_input = st.text_area("Or paste Job Description here", height=200)

analyze_btn = st.button("🔍 Analyze", use_container_width=True)


# ----------------- ANALYZE FLOW -------------
if analyze_btn:
    if not resume_file:
        st.error("Please upload your **Resume** first.")
        st.stop()

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
            st.error(f"Could not read JD: {e}")
            st.stop()

    if not raw_jd and not jd_text_input.strip():
        st.error("Please provide a Job Description (file or paste).")
        st.stop()

    if not raw_jd:
        raw_jd = jd_text_input

    with st.spinner("Analyzing…"):
        resume_text = clean_text(raw_resume)
        jd_text = clean_text(raw_jd)

        jd_keywords = extract_keywords(jd_text, top_n=40)

        matched, missing = keyword_gaps(resume_text, jd_keywords)
        score = score_resume(resume_text, jd_text, matched, missing)

        suggestions = []
        if missing:
            suggestions.append(f"Add missing keywords: {', '.join(missing[:10])}")
        if len(matched) < 10:
            suggestions.append("Use more action verbs and metrics.")
        suggestions.append("Tailor skills to match JD phrasing.")

    st.success("✅ Analysis complete!")
    st.metric("Overall Score", f"{round(score, 1)} / 100")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("✅ Matched")
        st.write(", ".join(matched) if matched else "—")
    with c2:
        st.subheader("❌ Missing")
        st.write(", ".join(missing) if missing else "—")

    st.subheader("💡 Suggestions")
    for s in suggestions:
        st.write(f"- {s}")

    report = make_report(resume_text, jd_text, score, matched, missing, suggestions)
    st.download_button(
        "📄 Download Report",
        data=report.encode("utf-8"),
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.caption("Built with Streamlit. Always tailor your resume truthfully to each role.")
