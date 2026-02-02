import streamlit as st
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go

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


'''def stage_selector():
    return st.selectbox(
        "Interview Stage",
        ["Screening Call", "Technical Round 1", "System Design", "Managerial/Final"],
        index=1
    )'''


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

def render_radar_chart(candidate_scores, jd_expectations):
    """
    Renders the Compatibility Radar Chart with dual traces: Candidate vs JD Expectations.
    Highlights critical gaps (> 0.3).
    
    :param candidate_scores: Dict { 'Backend': 0.8, 'Frontend': 0.5 ... }
    :param jd_expectations: Dict { 'Backend': 1.0, 'Frontend': 0.7 ... }
    """
    if not candidate_scores or not jd_expectations:
        st.info("No data for Radar Chart.")
        return

    categories = list(candidate_scores.keys())
    candidate_values = [candidate_scores[cat] for cat in categories]
    expectation_values = [jd_expectations[cat] for cat in categories]
    
    # Calculate gaps
    gaps = [expectation_values[i] - candidate_values[i] for i in range(len(categories))]
    critical_gaps = [(cat, gap) for cat, gap in zip(categories, gaps) if gap >= 0.3]
    
    # Close the loop for the radar chart
    if categories:
        categories_loop = categories + [categories[0]]
        candidate_values_loop = candidate_values + [candidate_values[0]]
        expectation_values_loop = expectation_values + [expectation_values[0]]
    
    fig = go.Figure()
    
    # Trace 1: Candidate Scores (blue, solid)
    fig.add_trace(go.Scatterpolar(
        r=candidate_values_loop,
        theta=categories_loop,
        fill='toself',
        name='Candidate Score',
        line_color='rgba(0, 123, 255, 1)',
        fillcolor='rgba(0, 123, 255, 0.3)',
        hovertemplate='<b>%{theta}</b><br>Candidate: %{r:.2f}<extra></extra>'
    ))
    
    # Trace 2: JD Expectations (red, dashed)
    fig.add_trace(go.Scatterpolar(
        r=expectation_values_loop,
        theta=categories_loop,
        fill='toself',
        name='JD Requirement',
        line=dict(color='rgba(255, 0, 0, 0.7)', dash='dash'),
        fillcolor='rgba(255, 0, 0, 0.1)',
        hovertemplate='<b>%{theta}</b><br>JD Requirement: %{r:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        legend=dict(x=1.1, y=1),
        margin=dict(l=60, r=120, t=60, b=40),
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show critical gaps summary
    if critical_gaps:
        st.warning(f"⚠️ **Critical Gaps ({len(critical_gaps)}/{len(categories)})**: Candidate below JD requirement by >0.3")
        for cat, gap in critical_gaps:
            st.markdown(f"  - **{cat}**: {gap:.2f} gap (Candidate: {candidate_scores[cat]:.2f} vs JD: {jd_expectations[cat]:.2f})")
    else:
        st.success(f"✅ **No Critical Gaps**: All skills within acceptable range (<0.3 gap)")



def render_audit_report(report_text):
    """Renders the textual audit report with styling."""
    st.markdown("### 📋 Grounded Audit Report")
    st.info(report_text)
