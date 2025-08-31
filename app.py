import streamlit as st
from datetime import datetime
from typing import List

# ---- Project imports ----
from parser import read_pdf, read_docx
from utils import clean_text, extract_keywords
from scorer import score_resume
from analyzer import keyword_gaps

# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="logo.png",   # <- our logo
    layout="centered",
)

# ------------------- HEADER ----------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=60)
with col2:
    st.title("AI Resume Analyzer")
st.caption("Match your resume to a Job Description, see keyword gaps, and get suggestions.")

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

# --------------- SMALL HELPERS -------------
def read_any(file) -> str:
    if file is None:
        return ""
    data = file.read()
    mime = file.type or ""

    if "pdf" in mime:
        return read_pdf(data)
    if "word" in mime or file.name.lower().endswith(".docx"):
        return read_docx(data)
    if "text" in mime or file.name.lower().endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    return ""

def to_lines(items: List[str]) -> str:
    return "\n".join(f"• {x}" for x in items)

def make_report(resume_text, jd_text, score, matched, missing, suggestions):
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
"""
    return report

# ------------------- MAIN UI ----------------
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
with col2:
    jd_file = st.file_uploader("Optional: Upload JD", type=["pdf", "docx", "txt"])

jd_text_input = st.text_area("Or paste Job Description here", height=200)

analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# ----------------- ANALYZE FLOW -------------
if analyze_btn:
    if not resume_file:
        st.error("Please upload your Resume file first.")
        st.stop()

    raw_resume = read_any(resume_file)
    raw_jd = read_any(jd_file) if jd_file else jd_text_input

    if not raw_jd.strip():
        st.error("Please add a Job Description (upload or paste).")
        st.stop()

    with st.spinner("Analyzing…"):
        resume_text = clean_text(raw_resume)
        jd_text = clean_text(raw_jd)

        jd_keywords = extract_keywords(jd_text, top_n=40)
        matched, missing = keyword_gaps(resume_text, jd_keywords)
        score = score_resume(resume_text, jd_text, matched, missing)

        suggestions: List[str] = []
        if missing:
            suggestions.append(f"Add context for missing keywords: {', '.join(missing[:10])}")
        if len(matched) < 10:
            suggestions.append("Highlight outcomes with metrics (%, $, time saved).")
        suggestions.append("Mirror key phrases from the JD in your resume where true.")

    # Results
    st.success("Analysis complete!")
    st.metric(label="Score", value=f"{round(score, 1)} / 100")
    st.progress(min(max(score / 100.0, 0.0), 1.0))

    st.markdown("### ✅ Matched Keywords")
    st.write(", ".join(matched) if matched else "—")

    st.markdown("### ❗ Missing Keywords")
    st.write(", ".join(missing) if missing else "—")

    st.markdown("### 💡 Suggestions")
    for s in suggestions:
        st.write(f"- {s}")

    report_text = make_report(resume_text, jd_text, score, matched, missing, suggestions)
    st.download_button(
        "📄 Download Report",
        data=report_text.encode("utf-8"),
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ----------------- FOOTER -------------------
st.divider()
st.caption("Built with Streamlit. Always tailor your resume truthfully to the role.")
