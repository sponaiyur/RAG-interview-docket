import requests
import tempfile
import os
import sys
from pathlib import Path
from core.chunker.chunker import AgenticChunker
from core.question_engine.generator import generate_questions_from_chunks
from core.parser.resume_parser import parse_resume_to_dict
from core.audit.scorer import Scorer
from core.audit.auditor import Auditor
from core.chunker.skill_extractor import JDSkillExtractor

if sys.platform=="win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

def parse_resume_api(resume_file):
    """
    Try to parse resume locally since backend is likely missing.
    """
    try:
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resume_file.getvalue())
            tmp_path = Path(tmp.name)
        
        # Parse locally
        resume_data = parse_resume_to_dict(tmp_path)
        
        # Cleanup
        os.remove(tmp_path)
        
        return resume_data

    except Exception as e:
        print(f"Local parsing failed: {e}")
        return None


def generate_questions_local(resume_json, jd_text):
    """
    Local implementation of question generation pipeline.
    1. Chunk resume based on JD skills (AgenticChunker)
    2. Generate questions for each chunk (QuestionGenerator)
    """
    
    try:
        print("Starting local question generation...")
        # 1. Chunking
        print("1. Chunking resume based on JD...")
        chunker = AgenticChunker(resume_json)
        chunks = chunker.chunk_by_skills(jd_text=jd_text)
        
        if not chunks:
            print("No chunks generated")
            return []
        
        print(f"Generated {len(chunks)} chunks. Starting question generation...")

        # 2. Question Generation
        # chunks is a list of dicts
        # Return the generator directly
        return generate_questions_from_chunks(chunks)

    except Exception as e:
        print(f"Error in local question generation: {e}")
        return None


def run_audit_pipeline(chunks, jd_text):
    """
    Runs the Grounded Auditor pipeline.
    """
    try:
        print("Starting Auditor Pipeline...")
        # Extract skills for Taxonomy mapping
        extractor = JDSkillExtractor()
        jd_skills = extractor.extract_skills(jd_text)
        
        # Scoring
        scorer = Scorer(chunks, jd_skills, jd_text)
        scores = scorer.compute_scores()
        
        # LLM Audit
        auditor = Auditor(scores)
        closure_report = auditor.generate_closure()
        
        # Return structured data
        return {
            "scores": scores,
            "report": closure_report
        }
        
    except Exception as e:
        print(f"Audit pipeline failed: {e}")
        return None
