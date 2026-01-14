import requests

BACKEND_URL = "http://localhost:8000"  # change when deployed


def parse_resume_api(resume_file):
    """
    Calls Intern-1 backend service: Resume (PDF/DOCX) -> Structured JSON
    """
    try:
        files = {
            "file": (resume_file.name, resume_file.getvalue())
        }
        resp = requests.post(f"{BACKEND_URL}/parse_resume", files=files, timeout=60)

        if resp.status_code != 200:
            return None

        return resp.json()

    except Exception:
        return None


def generate_questions_api(resume_json, jd_text, interview_stage):
    """
    Calls Intern-2 + Intern-3 backend service:
    (Resume JSON + JD) -> Questions JSON
    """
    try:
        payload = {
            "resume_json": resume_json,
            "jd_text": jd_text,
            "interview_stage": interview_stage
        }

        resp = requests.post(
            f"{BACKEND_URL}/generate_questions",
            json=payload,
            timeout=60
        )

        if resp.status_code != 200:
            return None

        return resp.json()

    except Exception:
        return None
