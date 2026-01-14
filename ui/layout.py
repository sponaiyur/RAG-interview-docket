import streamlit as st
from services.pipeline_client import parse_resume_api, generate_questions_api


def render_app():
    st.title("🧠 Interview Docket Generator")
    st.caption("AI-assisted. Human-controlled. No automation.")

    st.sidebar.title("📌 Inputs")

    resume_file = st.sidebar.file_uploader(
        "Upload Resume (PDF/DOCX)",
        type=["pdf", "docx"]
    )

    jd_text = st.sidebar.text_area(
        "Paste Job Description (JD)",
        placeholder="Paste the full JD here...",
        height=200
    )

    interview_stage = st.sidebar.selectbox(
        "Interview Stage",
        ["Screening", "Technical", "System Design", "Final"]
    )

    st.sidebar.info("AI suggests questions. Interviewer stays in control.")

    # Session state init
    if "resume_json" not in st.session_state:
        st.session_state.resume_json = None

    if "questions" not in st.session_state:
        st.session_state.questions = None

    # Manual trigger (nothing happens automatically)
    if st.button("🚀 Generate Questions"):
        if not resume_file:
            st.error("Please upload a resume file.")
            return

        if not jd_text.strip():
            st.error("Please paste the Job Description (JD).")
            return

        with st.spinner("Parsing resume on server..."):
            resume_json = parse_resume_api(resume_file)

        if resume_json is None:
            st.error("Resume parsing failed.")
            return

        st.session_state.resume_json = resume_json

        with st.spinner("Generating questions (Resume + JD)..."):
            questions = generate_questions_api(
                resume_json=resume_json,
                jd_text=jd_text,
                interview_stage=interview_stage
            )

        if questions is None:
            st.error("Question generation failed.")
            return

        st.session_state.questions = questions
        st.success("Questions generated successfully!")

    # Output rendering
    if st.session_state.resume_json:
        st.subheader("📄 Parsed Resume (Structured JSON)")
        st.json(st.session_state.resume_json)

    if st.session_state.questions:
        st.subheader("🤖 Suggested Questions")
        for i, q in enumerate(st.session_state.questions):
            with st.container():
                st.markdown(f"**Claim:** {q.get('claim', '')}")
                st.markdown(f"**Question:** {q.get('question', '')}")
                st.caption(f"Why this question? → {q.get('reason', '')}")
                st.divider()

    st.info(
        "⚠️ Ethical Boundary: This tool does NOT evaluate candidates. "
        "It only helps interviewers ask better questions faster."
    )
