'''
prompts.py: Dedicated file to store all prompt templates
'''
# JD Skill extractor prompt
import json

def skill_extractor_prompt(jd_text: str):
    return f"""TASK: Extract technical skills from a Job Description.
    
            INSTRUCTIONS:
            - Return ONLY valid JSON array format
            - Start with [ and end with ]
            - Each skill name in double quotes
            - Separated by commas
            - NO other text before or after

            INPUT:
            {jd_text}

            OUTPUT:"""

def chunker_prompt(target_skills: str, resume: str):
    resume_str = json.dumps(resume, indent=2)
    
    return f"""
        You are an expert Technical Recruiter and Engineer.
        
        TASK:
        Analyze the provided RESUME data against the list of TARGET SKILLS.
        For each Target Skill, aggregate evidence from the resume.
        
        TARGET SKILLS: {target_skills}
        
        RESUME DATA:
        {resume_str}
        
        RULES:
        1. Look for SEMANTIC matches. (e.g., "Scikit-learn" implies "Machine Learning").
        2. Look for IMPLIED skills. (e.g., "API endpoints" implies "Backend").
        3. If a claim supports multiple skills, duplicate it into both chunks.
        4. Generate a 'reasoning' field: Why does this claim support this skill?
        
        Analyze deeply and return the structured analysis.
        """

def auditor(context: str):
    return f"""
        You are the 'Grounded Auditor' for a technical interview process.
        Your goal is to provide a GAP ANALYSIS report based on pure evidence.

        RULES:
        1. NO JUDGMENT: Do not use words like "good", "bad", "smart", "failed".
        2. DATA-DRIVEN: Reference specific categories (Backend, AI/ML) and their evidence status.
        3. ADMINISTRATIVE EMPATHY: Frame gaps as "missing evidence" rather than "incompetence".
        4. FORMAT: Use a clear, professional tone. Add a 'Verdict' section: "Proceed to Interview" or "Hold".

        CANDIDATE ALIGNMENT DATA:
        {context}

        Generate a brief (3-4 bullet points) Closing Report and a Verdict.
        """

def jd_bucketing(jd,extracted_skills) :

        return f"""
        You are a Technical Recruiter's Assistant. Your task is to analyze a Job Description and categorize extracted skills into logical buckets.

        INPUT:
        1. JD Text: {jd}
        2. Extracted Skills: {extracted_skills}

        TASK:
        1. Group the extracted skills into logical buckets (e.g., "Languages", "Databases", "Cloud").
        2. Determine if the bucket/skill falls under "Minimum Requirements" (CORE) or "Preferred Qualifications" (PREFERRED) based on the JD structure.
        3. Handle "OR" logic: If the JD says "Python or Java", put them in the same, relevant bucket.

        Analyse thoroughly, and respond accurately.
        """