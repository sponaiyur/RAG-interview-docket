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