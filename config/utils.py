'''
utils.py: Utility functions for configuration and data loading
'''

import os
import json
from pathlib import Path


def load_jd(jd_text: str) -> str:
    """
    Validate and return Job Description text from Streamlit input.
    """

    if not jd_text or not jd_text.strip():
        raise ValueError("Job Description cannot be empty")
    
    return jd_text.strip()


def load_jd_from_dir(jd_path: str = None) -> str:
    """
    Load Job Description text from file.
    """
    if jd_path is None:
        # Default to data/jd directory, get most recent file
        jd_dir = Path("data/jd")
        if not jd_dir.exists():
            raise FileNotFoundError(f"JD directory not found: {jd_dir}")
        
        # Get all .txt files in the directory
        jd_files = list(jd_dir.glob("*.txt"))
        if not jd_files:
            raise FileNotFoundError(f"No .txt files found in {jd_dir}")
        
        # Get the most recently modified file
        jd_path = max(jd_files, key=os.path.getmtime)
    
    jd_path = Path(jd_path)
    if not jd_path.exists():
        raise FileNotFoundError(f"JD file not found: {jd_path}")
    
    with open(jd_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_parsed_resume(resume_path: str = None) -> dict:
    """
    Load parsed resume JSON from data/resumes/parsed/.
    """
    if resume_path is None:
        # Default to data/resumes/parsed directory, get most recent file
        resume_dir = Path("data/resumes/parsed")
        if not resume_dir.exists():
            raise FileNotFoundError(f"Resume directory not found: {resume_dir}")
        
        # Get all .json files in the directory
        resume_files = list(resume_dir.glob("*.json"))
        if not resume_files:
            raise FileNotFoundError(f"No .json files found in {resume_dir}")
        
        # Get the most recently modified file
        resume_path = max(resume_files, key=os.path.getmtime)
    
    resume_path = Path(resume_path)
    if not resume_path.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")
    
    with open(resume_path, 'r', encoding='utf-8') as f:
        return json.load(f)
