import streamlit as st
from datetime import datetime
from pathlib import Path

def header():
    st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stButton button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
        }
        .question-card {
            background-color: white;
            color: #31333F; /* Enforce dark text for white card */
            padding: 0.8rem;
            margin-top: 0.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .claim-box {
            background-color: #f0f2f6;
            color: #31333F; /* Enforce dark text for grey box */
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            border-left: 4px solid #FF4B4B;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("🧠") # Placeholder for logo
    with col2:
        st.title("Interview Docket")
        st.markdown("*AI-Assisted. Human-Controlled. Precision Engineering.*")
    st.divider()


def upload_resume():
    st.markdown("### 📄 Candidate Resume")
    return st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"], label_visibility="collapsed")


def upload_jd():
    st.markdown("### 📋 Job Description")
    return st.text_area(
        "Job Description",
        placeholder="Paste the full Job Description (JD) here...",
        height=300,
        label_visibility="collapsed"
    )


def stage_selector():
    return st.selectbox(
        "Interview Stage",
        ["Screening Call", "Technical Round 1", "System Design", "Managerial/Final"],
        index=1
    )


def generate_button():
    return st.button("🚀 GENERATE INTERVIEW DOCKET")


def show_resume_json(resume_json):
    with st.expander("🔍 Debug: View Parsed Resume Data"):
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

def show_questions(chunks_output):
    """
    Render questions from the nested structure with professional styling.
    """
    st.markdown("## 🤖 Generated Interview Docket")
    
    if not chunks_output:
        st.info("No questions generated yet. Start the process above.")
        return

    for chunk in chunks_output:
        skill = chunk.get("focus_skill", "General")
        
        # Use a styled container for each skill section
        with st.container():
            st.markdown(f"### ⚡ {skill}")
            
            for result in chunk.get("results", []):
                claim = result.get("claim", "")
                claim_type = result.get("claim_type", "General")
                
                # Custom HTML for Claim Box
                st.markdown(f"""
                <div class="claim-box">
                    <strong>Target Claim ({claim_type}):</strong><br>
                    <em>"{claim}"</em>
                </div>
                """, unsafe_allow_html=True)
                
                # Questions with visual hierarchy
                for q in result.get("questions", []):
                    level = q.get("level", "question").replace("_", " ").title()
                    text = q.get("question", "")
                    
                    st.markdown(f"""
                    <div class="question-card">
                        <small style="color: #666; font-weight: bold; text-transform: uppercase;">{level}</small><br>
                        {text}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")


def ethics_banner():
    st.markdown("---")
    st.caption(
        "⚠️ **Ethical Boundary**: This tool assists in question formulation but does not evaluate candidates. "
        "The interviewer is responsible for the final assessment."
    )
