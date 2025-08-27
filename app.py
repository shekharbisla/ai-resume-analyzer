import streamlit as st
from io import BytesIO
from src.parser import read_pdf, read_docx
from src.analyzer import analyze

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="centered")

st.title("🤖 AI Resume Analyzer")
st.write("Upload your **Resume (PDF/DOCX)** and paste the **Job Description** to get a match score, missing skills, and improvement tips.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
with col2:
    file_type = st.selectbox("Resume Type", ["pdf", "docx"])

job_desc = st.text_area("Paste Job Description", height=180, placeholder="Paste the JD here...")

if st.button("Analyze Resume", type="primary"):
    if not resume_file or not job_desc.strip():
        st.error("Please upload a resume and paste a job description.")
    else:
        bytes_data = resume_file.read()
        try:
            if file_type == "pdf":
                resume_text = read_pdf(bytes_data)
            else:
                resume_text = read_docx(bytes_data)
        except Exception as e:
            st.error(f"Couldn't read the file: {e}")
            st.stop()

        result = analyze(resume_text, job_desc)

        st.subheader("🔢 Match Score")
        st.metric("Keyword Coverage", f"{result['coverage']['score']}%")

        st.subheader("✅ Skills Match")
        st.write("**Overlap:** ", ", ".join(result["skills_overlap"]) or "–")
        st.write("**Missing (from JD):** ", ", ".join(result["skills_missing"]) or "–")

        with st.expander("🔍 Keywords found from JD"):
            st.write(", ".join(result["coverage"]["found"]) or "–")

        with st.expander("🧩 Keywords missing from JD (top)"):
            st.write(", ".join(result["coverage"]["missing"]) or "–")

        st.subheader("🛠️ Quick Tips")
        for t in (result["tips"] or ["Looks good! Make sure keywords appear in measurable bullet points."]):
            st.write("•", t)

        # Downloadable report
        report = f"""AI Resume Analyzer Report

Score: {result['coverage']['score']}%
Overlap Skills: {", ".join(result['skills_overlap'])}
Missing Skills: {", ".join(result['skills_missing'])}

Tips:
- """ + "\n- ".join(result["tips"] or ["Looks good!"])

        st.download_button("⬇️ Download Report (.txt)", data=report.encode("utf-8"),
                           file_name="resume_report.txt", mime="text/plain")
