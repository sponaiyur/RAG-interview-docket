import streamlit as st
from ui import components as c
from core.pipeline_client import parse_resume_api, generate_questions_api


def render_app():
    c.header()

    st.sidebar.title("📌 Inputs")
    resume_file = c.upload_resume()
    jd_text = c.upload_jd()
    interview_stage = c.stage_selector()

    st.sidebar.info("AI suggests questions. Interviewer stays in control.")

    if c.generate_button():
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

        with st.spinner("Generating questions..."):
            questions = generate_questions_api(resume_json, jd_text, interview_stage)

        if questions is None:
            st.error("Question generation failed.")
            return

        st.session_state.questions = questions
        st.success("Questions generated successfully!")

    # Display outputs
    if st.session_state.resume_json:
        c.show_resume_json(st.session_state.resume_json)

    if st.session_state.questions:
        c.show_questions(st.session_state.questions)

    c.ethics_banner()
