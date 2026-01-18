import requests
import tempfile
import os
from pathlib import Path
from core.chunker.chunker import AgenticChunker
from core.question_engine.generator import generate_questions_from_chunks
from core.parser.resume_parser import parse_resume_to_dict

BACKEND_URL = "http://localhost:8000"

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


def generate_questions_local(resume_json, jd_text, interview_stage):
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
