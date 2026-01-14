import requests

BACKEND_URL = "http://localhost:8000"

def parse_resume_api(resume_file):
    try:
        files = {"file": (resume_file.name, resume_file.getvalue())}
        resp = requests.post(f"{BACKEND_URL}/parse_resume", files=files, timeout=60)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def generate_questions_api(resume_json, jd_text, interview_stage):
    try:
        payload = {
            "resume_json": resume_json,
            "jd_text": jd_text,
            "interview_stage": interview_stage
        }
        resp = requests.post(f"{BACKEND_URL}/generate_questions", json=payload, timeout=60)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None
