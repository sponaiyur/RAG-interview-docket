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
        2. DATA-DRIVEN: Reference specific buckets and detail their evidence status against the JD EXPECTATION (not the full skill list).
        3. EXPECTATION vs SKILL LIST: The "Expectation" field tells you what the JD ACTUALLY requires. The skill list is just context.
           - If Expectation says "ATLEAST ONE", candidate only needs one skill from that list. Judge them against that.
           - If Expectation says "Must know ALL", then judge against all skills.
        4. ADMINISTRATIVE EMPATHY: Highlight their strengths. Frame gaps as "missing evidence" rather than "incompetence".
        5. When evaluating the candidate, take a difference between the expected vs candidate scre, advise accordingly.
        6. FORMAT: Use a clear, professional tone. Add a 'Verdict' section: "Proceed to Interview" or "Hold".

        CANDIDATE ALIGNMENT DATA:
        {context}

        Generate a brief (3-4 bullet points) Closing Report and a Verdict based on the EXPECTATION field, not the full skill lists.
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
        4. FOR EACH BUCKET, analyze the JD language and set expected_score (0.0-1.0):
           - If JD says "must know ALL skills": expected_score = 1.0
           - If JD says "proficiency in ATLEAST ONE": expected_score = 1.0 / count(skills)
           - If PREFERRED bucket: expected_score = 0.7
           - Use the actual phrasing from the JD to determine the expectation.

        Analyse thoroughly, and respond accurately.
        """