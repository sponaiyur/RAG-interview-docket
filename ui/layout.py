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
                st.info("Questions will appear here after generation.")
        
        with tab2:
            if st.session_state.resume_json:
                c.show_resume_json(st.session_state.resume_json)

    if not st.session_state.resume_json and not st.session_state.questions:
        # Welcome State
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
            st.error("Resume parsing failed.")
            return
            
        status.update(label="Analysis Critical!", state="complete", expanded=False)

    st.session_state.resume_json = resume_json

    # Phase 2: Generation with Progress Bar
    progress_bar = st.progress(0, text="Starting Generation...")
    questions_placeholder = st.empty()
    results_map = {}
    
    questions_generator = generate_questions_local(resume_json, jd_text, interview_stage)
    
    if questions_generator:
        # Create a container for the streaming output
        with questions_placeholder.container():
            st.info("Generating questions... (This uses local AI and may take a moment)")
            
        for chunk_id, skill, result, current, total in questions_generator:
            # Update Progress
            percent = int((current / total) * 100)
            progress_bar.progress(percent, text=f"Generating Question {current}/{total} (Skill: {skill})")
            
            # Aggregate Results
            if chunk_id not in results_map:
                results_map[chunk_id] = {
                    "focus_skill": skill,
                    "results": []
                }
            results_map[chunk_id]["results"].append(result)
            
            # Update Session & Render
            st.session_state.questions = list(results_map.values())
            
            # We don't partial render inside the placeholder anymore because we switched to Tabs.
            # But we can show a preview or just let the user wait? 
            # Actually, user wants to see progress. Let's update the layout to show the questions appearing.
            # However, since we moved render logic to the main loop (Tabs), we need to trigger a rerun or update a placeholder.
            # The tabs are ONLY rendered if session state exists. Since we are updating session state, 
            # we can use a placeholder in the main area OR just rely on the placeholder we made.
            
            # Let's render the "Partial" questions in the placeholder for now, so they see movement.
            with questions_placeholder.container():
                 c.show_questions(st.session_state.questions)

        progress_bar.empty()
        questions_placeholder.empty() # Clear temporary placeholder to let the main Tab interface take over
        st.success("Generation Complete!")
        st.rerun() # Force a rerun to properly render the Tabs with full data
    else:
        st.error("Question generation failed.")
