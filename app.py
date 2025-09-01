import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from datetime import datetime
from typing import List
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.graph_objects as go

# ---- Project imports ----
from src.analyzer import keyword_gaps, default_suggestions
from src.utils import clean_text, extract_keywords
from src.scorer import score_resume
from src.parser import read_pdf, read_docx

# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="logo.png",
    layout="centered",
)

# ---------------- THEME TOGGLE ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme_choice = st.sidebar.radio("🎨 Theme", ["dark", "light"])
st.session_state.theme = theme_choice

def apply_theme():
    if st.session_state.theme == "dark":
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #0e1117;
                color: #f8f9fa;
            }
            .debug-card {
                background: linear-gradient(135deg, #1e1e2e, #121212);
                border: 1px solid #333;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 20px;
                color: #f8f9fa;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
            }
            h4 { color: #FFD700; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #f8f9fa;
                color: #212529;
            }
            .debug-card {
                background: linear-gradient(135deg, #ffffff, #f1f1f1);
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 20px;
                color: #212529;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            }
            h4 { color: #0d6efd; }
            </style>
            """,
            unsafe_allow_html=True,
        )

apply_theme()

# ------------------- HEADER ----------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=60)
with col2:
    st.title("AI Resume Analyzer")

st.caption("Match your resume to a Job Description, see keyword gaps, and get smart suggestions.")

# ------------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ How to use")
    st.markdown(
        "1) Upload your **Resume** (PDF/DOCX/TXT)\n"
        "2) Paste or upload the **Job Description**\n"
        "3) Click **Analyze** to see score & gaps\n"
        "4) Download the report\n\n"
        "✨ Founder: Bisla ji"
    )
    st.divider()
    st.caption("Tip: Use a tailored resume for each JD to improve your score.")

# Debug Mode option
show_debug = st.sidebar.checkbox("🔍 Debug Mode")

# --------------- HELPERS -------------
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
        suggestions = default_suggestions(matched, missing)

    # ---------------- RESULTS TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Score", "✅ Matched", "❗ Missing", "💡 Suggestions"])

    with tab1:
        st.subheader("Overall Match")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Resume Match Score"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green" if score > 50 else "red"}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Matched Keywords")
        if matched:
            wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(matched))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)
        else:
            st.write("—")

    with tab3:
        st.subheader("Missing Keywords")
        if missing:
            wc = WordCloud(width=800, height=400, background_color="black", colormap="Reds").generate(" ".join(missing))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)
        else:
            st.write("—")

    with tab4:
        st.subheader("Suggestions")
        for s in suggestions:
            st.info(s)

    # ---------------- DEBUG INFO ----------------
    if show_debug:
        st.subheader("🛠️ Debug Info")

        def debug_card(title, content):
            st.markdown(f"<div class='debug-card'><h4>{title}</h4>", unsafe_allow_html=True)
            st.json(content)

        debug_card("📌 Extracted JD Keywords", jd_keywords)
        debug_card("✅ Matched Keywords", matched)
        debug_card("❗ Missing Keywords", missing)

    # Report Download
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
st.markdown(
    "<p style='text-align:center; font-size:14px;'>"
    "🚀 Built with ❤️ using Streamlit | © 2025 AI Resume Analyzer<br>"
    "Crafted by <b>Bisla ji</b> | <a href='https://github.com/shekharbisla' target='_blank'>GitHub</a>"
    "</p>",
    unsafe_allow_html=True,
)
