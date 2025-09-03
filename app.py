import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from datetime import datetime
from typing import List
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.graph_objects as go

# --- NLTK Fix (auto download if missing) ---
import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

# ---- Project imports ----
from src.analyzer import keyword_gaps, default_suggestions
from src.utils import clean_text, extract_keywords
from src.scorer import score_resume
from src.parser import read_pdf, read_docx

# ---------------- UI CONFIG ----------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="logo.png",  # use optimized small PNG
    layout="centered",
)

# ---------------- CUSTOM CSS ----------------
def set_background(theme="dark"):
    if theme == "dark":
        bg_color = "#0e1117"
        text_color = "white"
        bg_image = "bg.png"
    else:
        bg_color = "#ffffff"
        text_color = "black"
        bg_image = "bg_light.png"  # Optional: ek light version bana lo

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('{bg_image}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: {text_color};
        }}

        h1, h2, h3, h4 {{
            color: #FFD700 !important;
        }}

        section[data-testid="stSidebar"] {{
            background: rgba(0,0,0,0.85);
            color: white;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, #ffb347, #ffcc33);
            color: black !important;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: linear-gradient(90deg, #ffcc33, #ffb347);
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------- CUSTOM STYLING ----------------
page_bg = """
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
    font-family: 'Poppins', sans-serif;
    color: #f5f5f5;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(20,20,20,0.95);
    color: #f5f5f5;
}

/* Headings */
h1, h2, h3, h4 {
    color: #FFD700 !important;
    font-weight: 700;
}

/* Upload boxes contrast */
.css-1cpxqw2, .stFileUploader, textarea {
    background-color: rgba(255,255,255,0.9) !important;
    color: black !important;
    border-radius: 8px;
    padding: 8px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #ffb347, #ffcc33);
    color: black !important;
    font-weight: bold;
    font-size: 16px;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ffcc33, #ffb347);
    color: white !important;
}

/* Tabs */
.stTabs [role="tablist"] button {
    font-size: 16px;
    padding: 10px 20px;
    font-weight: 600;
}

/* Suggestions box */
.stAlert {
    background: rgba(0,0,0,0.6) !important;
    color: #ffffff !important;
    border-radius: 10px;
    padding: 1rem;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.png", width=70)
with col2:
    st.markdown("<h1>🚀 AI Resume Analyzer</h1>", unsafe_allow_html=True)

st.caption("⚡ Crafted by Bisla Ji | Analyze • Improve • Get Hired")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.image("logo.png", width=60)
    st.markdown("### ⚡ AI Resume Analyzer v2.0")
    st.caption("Crafted with ❤️ by **Bisla Ji**")
    st.markdown("---")
    st.markdown("## ⚙️ How to use")
    st.markdown(
        "1) Upload your **Resume** (PDF/DOCX/TXT)\n"
        "2) Paste or upload the **Job Description**\n"
        "3) Click **Analyze** to see score & gaps\n"
        "4) Download the report and improve your resume"
    )
    st.divider()
    st.caption("💡 Pro Tip: Use a tailored resume for each JD to improve your score.")

# Debug Mode option
show_debug = st.sidebar.checkbox("🔍 Debug Mode (show extracted data)")

# ---------------- HELPERS ----------------
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

# ---------------- MAIN UI ----------------
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
with col2:
    jd_file = st.file_uploader("Optional: Upload JD", type=["pdf", "docx", "txt"])

jd_text_input = st.text_area("Or paste Job Description here", height=200)
analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# ---------------- ANALYZE FLOW ----------------
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

    # ---------------- RESULTS ----------------
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

    if show_debug:
        st.markdown("### 🛠️ Debug Info")
        st.json({
            "JD Keywords": jd_keywords,
            "Matched": matched,
            "Missing": missing
        })

    # Download button
    report_text = make_report(resume_text, jd_text, score, matched, missing, suggestions)
    st.download_button(
        "📄 Download Report",
        data=report_text.encode("utf-8"),
        file_name="resume_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ---------------- FOOTER ----------------
st.divider()
st.caption("⚡ Built with Streamlit | ✨ Premium UI | Crafted by Bisla Ji | Always tailor your resume truthfully to the role.")
