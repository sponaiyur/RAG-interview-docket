import json
from core.question_engine.llm_utils import call_llm

class Auditor:
    def __init__(self, scores):
        """
        :param scores: Output from Scorer.compute_scores()
                       { "radar_data": {...}, "detailed_scores": {...} }
        """
        self.radar_data = scores.get("radar_data", {})
        self.detailed_scores = scores.get("detailed_scores", {})

    def _format_score_context(self):
        """Converts scores to a readable context for the LLM."""
        lines = []
        for bucket, score in self.radar_data.items():
            status = "STRONG" if score > 0.7 else "MODERATE" if score > 0.4 else "MISSING EVIDENCE"
            lines.append(f"- {bucket}: {status} (Alignment: {int(score*100)}%)")
        return "\n".join(lines)

    def generate_closure(self):
        """
        Generates the 'Ethical Gap Analysis' using the LLM.
        """
        context = self._format_score_context()
        
        prompt = f"""
You are the 'Grounded Auditor' for a technical interview process.
Your goal is to provide a GAP ANALYSIS report based on pure evidence.

RULES:
1. NO JUDGMENT: Do not use words like "good", "bad", "smart", "failed".
2. DATA-DRIVEN: Reference specific categories (Backend, AI/ML) and their evidence status.
3. ADMINISTRATIVE EMPATHY: Frame gaps as "missing evidence" rather than "incompetence".
4. FORMAT: Use a clear, professional tone. Add a 'Verdict' section: "Proceed to Interview" or "Hold".

CANDIDATE ALIGNMENT DATA:
{context}

Generate a brief (3-4 bullet points) Closing Report and a Verdict.
"""
        return call_llm(prompt)
