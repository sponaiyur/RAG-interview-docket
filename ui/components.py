import streamlit as st

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
