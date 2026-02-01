import json
from core.question_engine.llm_utils import call_llm
from config.prompts import auditor

class Auditor:
    def __init__(self, scores):
        """
        :param scores: Output from Scorer.compute_scores()
                       { "radar_data": {...}, "detailed_scores": {...} }
        """
        self.radar_data = scores.get("radar_data", {})
        self.evidence_context = scores.get("evidence_context", {})
        # self.detailed_scores = scores.get("detailed_scores", {})

    def _format_score_context(self):
        """Converts scores to a readable context for the LLM."""
        lines = []
        for bucket, score in self.radar_data.items():
            sources = self.evidence_context.get(bucket, [])
            source_str=f" (Sources: {', '.join(sources)})" if sources else " (No concrete source found)"
            status = "STRONG" if score > 0.7 else "MODERATE" if score > 0.4 else "MISSING EVIDENCE"
            lines.append(f"- {bucket}: {status} (Alignment: {int(score*100)}%)")
        return "\n".join(lines)

    def generate_closure(self):
        """
        Generates the 'Ethical Gap Analysis' using the LLM.
        """
        context = self._format_score_context()
        
        prompt = auditor(context)
        return call_llm(prompt)
