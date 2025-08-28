# app.py
from __future__ import annotations

# Make ./src importable on Streamlit Cloud
import os, sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from datetime import datetime
from typing import List
import streamlit as st

from parser import read_pdf, read_docx
from utils import clean_text, extract_keywords
from scorer import score_resume
from analyzer import keyword_gaps

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="centered")
st.title("🧠 AI Resume Analyzer")
st.caption("Upload your resume + job description → get a match score, keyword gaps and quick suggestions.")

ALLOWED = ["pdf", "docx", "txt"]

def read_any(file) -> str:
    if file is None:
        return ""
    data = file.read()
    name = (file.name or "").lower()
    if name.endswith(".pdf"):
        return read_pdf(data)
    if name.endswith(".docx"):
        return read_docx(data)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    raise ValueError("Please upload PDF, DOCX or TXT")

def bullet(items: List[str]) -> str:
    return "\n".join(f"• {x}" for x in items)

def make_report(resume_text, jd_text, score, matched, missing, suggestions) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""AI Resume Analyzer Report
Generated: {ts}

Score: {score} / 100

Matched:
{bullet(matched) or "—"}

Missing:
{bullet(missing) or "—"}

Suggestions:
{bullet(suggestions) or "—"}
"""

with st.sidebar:
    st.markdown("## How to use")
    st.write("1) Upload Resume (PDF/DOCX/TXT)")
    st.write("2) Upload or paste Job Description")
    st.write("3) Click **Analyze** → Download report")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=ALLOWED)
with col2:
    jd_file = st.file_uploader("Upload JD (optional)", type=ALLOWED)

jd_text_input = st.text_area("…or paste Job Description", height=200, placeholder="Paste the JD here…")
analyze = st.button("🔍 Analyze", use_container_width=True)

if analyze:
    if not resume_file:
        st.error("Please upload your Resume first."); st.stop()

    try:
        resume_raw = read_any(resume_file)
    except Exception as e:
        st.error(f"Could not read resume: {e}"); st.stop()

    jd_raw = ""
    if jd_file:
        try:
            jd_raw = read_any(jd_file)
        except Exception as e:
            st.error(f"Could not read JD: {e}"); st.stop()
    if not jd_raw and not jd_text_input.strip():
        st.error("Please add a JD (upload or paste)."); st.stop()
    if not jd_raw:
        jd_raw = jd_text_input

    with st.spinner("Analyzing…"):
        resume_text = clean_text(resume_raw)
        jd_text = clean_text(jd_raw)

        jd_keywords = extract_keywords(jd_text, top_n=40)
        matched, missing = keyword_gaps(resume_text, jd_keywords)
        score = score_resume(resume_text, jd_text, matched, missing)

        suggestions: List[str] = []
        if missing:
            suggestions.append(f"Add missing keywords (only if true): {', '.join(missing[:10])}")
        if len(matched) < 10:
            suggestions.append("Use more action verbs and measurable outcomes.")
        suggestions.append("Mirror exact phrases from the JD in relevant bullets.")
        suggestions.append("Put the most relevant skills in the top section.")

    st.success("✅ Analysis complete!")
    st.metric("Overall Score", f"{score} / 100")

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
    st.download_button("📄 Download Report", report.encode("utf-8"),
                       file_name="resume_analysis.txt", mime="text/plain",
                       use_container_width=True)

st.caption("Built with Streamlit. Always tailor your resume truthfully to each role.")
