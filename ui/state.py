import streamlit as st

def init_state():
    """Initialize all session_state variables used in the app."""
    if "resume_json" not in st.session_state:
        st.session_state.resume_json = None

    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "jd_text" not in st.session_state:
        st.session_state.jd_text = ""

    if "interview_stage" not in st.session_state:
        st.session_state.interview_stage = "Screening"
