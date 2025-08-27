# app.py
import streamlit as st
from src.parser import read_pdf, read_docx
from src.scorer import similarity_and_gaps, bullet_suggestions

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="centered")
st.title("🧠 AI Resume Analyzer")
st.caption("Upload your resume (PDF/DOCX) and paste a Job Description to get a quick match score and suggestions.")

# --- Inputs
uploaded = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
jd_text = st.text_area("Paste Job Description", height=220, placeholder="Paste the JD here...")

def extract_text(file) -> str:
    name = (file.name or "").lower()
    data = file.read()
    if name.endswith(".pdf"):
        return read_pdf(data)
    if name.endswith(".docx"):
        return read_docx(data)
    raise ValueError("Unsupported file type")

col1, col2 = st.columns(2)
analyze = col1.button("🔍 Analyze")
reset = col2.button("♻️ Clear")

if reset:
    st.experimental_rerun()

if analyze:
    if not uploaded or not jd_text.strip():
        st.warning("Please upload a resume and paste the JD.")
    else:
        try:
            resume_text = extract_text(uploaded)
            res = similarity_and_gaps(resume_text, jd_text)
            st.subheader("Results")
            m1, m2 = st.columns(2)
            m1.metric("Similarity", f"{res['similarity']}%")
            m2.metric("Keyword Coverage", f"{res['coverage']}%")

            with st.expander("✅ Present keywords"):
                st.write(", ".join(res["present_keywords"]) or "—")

            with st.expander("❌ Missing keywords (add to resume if true)"):
                st.write(", ".join(res["missing_keywords"]) or "—")

            st.subheader("Suggested bullets to add")
            for b in bullet_suggestions(res["missing_keywords"]):
                st.markdown(f"- {b}")

            # Downloadable summary
            summary = [
                "AI Resume Analyzer Report",
                f"Similarity: {res['similarity']}%",
                f"Keyword coverage: {res['coverage']}%",
                f"Present keywords: {', '.join(res['present_keywords'])}",
                f"Missing keywords: {', '.join(res['missing_keywords'])}",
            ]
            st.download_button("⬇️ Download report (.txt)",
                               "\n".join(summary),
                               file_name="resume_report.txt")
        except Exception as e:
            st.error(f"Error: {e}")
