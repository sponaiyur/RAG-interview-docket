from core.question_engine.llm_utils import call_llm
from core.question_engine.classifier import classify_claim
from core.question_engine.dedup import deduplicate_by_level
import json

def generate_questions(claim: str):
    claim_type = classify_claim(claim)

    prompt = f"""
You are a technical interviewer.

CLAIM:
{claim}

CLAIM TYPE:
{claim_type}

Generate interview questions with STRICTLY DIFFERENT INTENTS.

You MUST generate exactly ONE question for each slot below.
DO NOT repeat meaning across questions.

Slots and constraints:

1. clarification
- Ask to clarify scope, responsibility, or vague wording
- DO NOT ask about design or decisions

2. base_overview
- Ask what was built and how it works at a high level

3. base_dataflow
- Ask about data flow or system components

4. depth_tradeoff
- Ask WHY design choices were made and trade-offs

5. depth_failure
- Ask about failure cases or limitations

6. follow_up_example
- Ask for a concrete real-world example

7. challenge_hypothetical
- Introduce a NEW scenario not mentioned in the claim

Return output STRICTLY as JSON:
[
  {{ "level": "...", "question": "..." }}
]
"""
    raw_text = call_llm(prompt)

    try:
        raw_questions = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback or simple error handling
        # For now, let's just return empty list or re-raise
        # Ideally we might retry or log
        raise ValueError("LLM did not return valid JSON")

    questions = deduplicate_by_level(raw_questions)


    return {
        "claim": claim,
        "claim_type": claim_type,
        "questions": questions
    }
