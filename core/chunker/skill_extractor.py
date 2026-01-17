'''
skill_extractor.py : Contains the JDSkillExtractor class, which accepts a JD and extracts skills from it
'''
# fix module import issues, delete later when running from app.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import json
import re
from groq import Groq
from config.prompts import skill_extractor_prompt
from config.settings import API_KEY, JD_SKILL_MODEL

class JDSkillExtractor:
    def __init__(self):
        self.client = Groq(api_key=API_KEY)
        self.model = JD_SKILL_MODEL

    def extract_skills(self, jd):
        prompt= skill_extractor_prompt(jd)
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        response_text = response.choices[0].message.content.strip()
        # try this out first, later add direct json parse

        # Extract JSON array from response (handles extra text)
        try:
            match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                skills = json.loads(json_str)
                if isinstance(skills, list):
                    return [str(skill).strip() for skill in skills if skill]
        except:
            pass

        # Extract quoted strings as fallback
        try:
            quoted = re.findall(r'"([^"]+)"', response_text)
            skills = [s.strip() for s in quoted if len(s.strip()) > 2]
            if skills:
                return skills
        except:
            pass

        return [] # If all else fails, you'll get empty list