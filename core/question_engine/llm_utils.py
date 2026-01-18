import subprocess
import re

USE_OLLAMA = True
MODEL_NAME = "qwen2.5:latest"


def call_llm(prompt: str) -> str:
    """
    Unified LLM call interface (currently uses Ollama).
    """
    if not USE_OLLAMA:
        return ""

    cmd = ["ollama", "run", MODEL_NAME]
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True
    )

    return result.stdout.strip()


def rephrase_question(question: str, claim: str, intent: str) -> str:
    prompt = f"""
You are refining an interview question.

Rules:
- Preserve the original intent exactly
- Do NOT generalize
- Do NOT merge with other questions

Claim:
{claim}

Intent:
{intent}

Original question:
{question}

Return only the rephrased question.
"""
    return call_llm(prompt)


def is_vague_claim(claim: str) -> bool:
    prompt = f"""
Is the following resume claim vague?

Answer ONLY YES or NO.

Claim:
{claim}
"""
    answer = call_llm(prompt)
    answer = re.sub(r"[^A-Z]", "", answer.upper())
    return answer == "YES"
