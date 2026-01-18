import streamlit as st
from ui import components as c
from core.pipeline_client import parse_resume_api, generate_questions_local


def render_app():
    st.set_page_config(page_title="Interview Docket", page_icon="🧠", layout="wide")
    
    # Sidebar for Inputs
    with st.sidebar:
        st.title("🧠 Interview Docket")
        st.caption("AI-Assisted. Human-Controlled.")
        st.divider()
        
        resume_file = c.upload_resume()
        jd_text = c.upload_jd()
        interview_stage = c.stage_selector()
        
        st.divider()
        generate_btn = c.generate_button()
        
        st.markdown("---")
        st.info("Input a Resume and JD to generate a custom interview script.")

    # Main Area
    if generate_btn:
        start_generation(resume_file, jd_text, interview_stage)

    # Persistent Display Logic
    # We use Tabs for better organization
    if st.session_state.resume_json or st.session_state.questions:
        tab1, tab2 = st.tabs(["🚀 Interview Questions", "📊 Source Analysis"])
        
        with tab1:
            if st.session_state.questions:
                c.show_questions(st.session_state.questions)
            else:
                st.info("Questions will appear here shortly...")
        
        with tab2:
            if st.session_state.resume_json:
                c.show_resume_json(st.session_state.resume_json)

    elif not generate_btn: # Show welcome only if not generating and no results
        st.markdown("## 👋 Welcome")
        st.markdown("""
        **RAG Interview Docket** helps you prepare for technical interviews by analyzing resumes against job descriptions.
        
        **To get started:**
        1. Upload a Candidate's Resume (PDF) in the sidebar.
        2. Paste the Job Description.
        3. Click **Generate**.
        """)

def start_generation(resume_file, jd_text, interview_stage):
    if not resume_file:
        st.sidebar.error("Please upload a resume file.")
        return

    if not jd_text.strip():
        st.sidebar.error("Please paste the Job Description (JD).")
        return

    # Phase 1: Preparation
    with st.status("Phase 1: Analyzing Documents...", expanded=True) as status:
        st.write("📂 Saving Job Description...")
        c.save_jd_to_dir(jd_text)
        
        st.write("📄 Parsing Resume...")
        resume_json = parse_resume_api(resume_file)
        
        if resume_json is None:
            status.update(label="Resume Parsing Failed", state="error")
            st.error("Resume parsing failed. Check logs.")
            return
            
        status.update(label="Analysis Critical!", state="complete", expanded=False)

    st.session_state.resume_json = resume_json

    # Phase 2: Generation with Progress Bar
    progress_exec = st.progress(0, text="Initializing AI...")
    questions_placeholder = st.empty()
    results_map = {}
    
    questions_generator = generate_questions_local(resume_json, jd_text, interview_stage)
    
    if questions_generator:
        with questions_placeholder.container():
             st.info("Starting Generation Engine...")

        for chunk_id, skill, result, current, total in questions_generator:
            # Update Progress
            percent = int((current / total) * 100)
            progress_exec.progress(percent, text=f"Generating: {skill} ({current}/{total})")
            
            # Aggregate Results
            if chunk_id not in results_map:
                results_map[chunk_id] = {
                    "focus_skill": skill,
                    "results": []
                }
            results_map[chunk_id]["results"].append(result)
            
            # Update Session & Render
            st.session_state.questions = list(results_map.values())
            
            # Render Preview
            with questions_placeholder.container():
                 c.show_questions(st.session_state.questions)

        progress_exec.progress(100, text="Generation Complete!")
        questions_placeholder.empty() # Clear placeholder
        st.balloons()
        st.rerun() # Force rerun to show final tabs
    else:
        st.error("Question generation failed.")
