import streamlit as st
from datetime import datetime
from pathlib import Path

def header():
    st.title("🧠 Interview Docket Generator")
    st.caption("AI-assisted. Human-controlled. No automation.")


def upload_resume():
    st.subheader("Upload Resume")
    return st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])


def upload_jd():
    st.subheader("Job Description (JD)")
    return st.text_area(
        "Paste Job Description",
        placeholder="Paste the full JD here...",
        height=200
    )


def stage_selector():
    st.subheader("Interview Stage")
    return st.selectbox(
        "Select Stage",
        ["Screening", "Technical", "System Design", "Final"]
    )


def generate_button():
    return st.button("🚀 Generate Questions")


def show_resume_json(resume_json):
    st.subheader("📄 Parsed Resume (Server Output)")
    st.json(resume_json)

def save_jd_to_dir(jd_text: str) -> str:
    """
    Save JD to data/jd/ with timestamp in filename.
    Returns the file path.
    """
    jd_dir = Path("data/jd")
    jd_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jd_{timestamp}.txt"
    filepath = jd_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(jd_text)
    
    return str(filepath)

def show_questions(questions):
    st.subheader("🤖 Suggested Questions")
    for idx, q in enumerate(questions):
        with st.container():
            st.markdown(f"**Claim:** {q.get('claim', '')}")
            st.markdown(f"**Question:** {q.get('question', '')}")
            st.caption(f"Why this question? → {q.get('reason', '')}")
            st.divider()


def ethics_banner():
    st.info(
        "⚠️ Ethical Boundary: This tool does NOT evaluate candidates. "
        "It only helps interviewers ask better questions faster."
    )
