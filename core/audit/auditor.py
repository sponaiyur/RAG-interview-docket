import json
from core.question_engine.llm_utils import call_llm
from config.prompts import auditor
from groq import Groq
from config import settings

class Auditor:
    def __init__(self, scores):
        """
        :param scores: Output from Scorer.compute_scores()
                       { "radar_data": {...}, "jd_expectations": {...}, "bucket_schema": [...], "detailed_scores": {...} }
        """
        self.radar_data = scores.get("radar_data", {})
        self.jd_expectations = scores.get("jd_expectations", {})
        self.evidence_context = scores.get("evidence_context", {})
        self.client=Groq(api_key=settings.API_KEY)
        self.bucket_schema = scores.get("bucket_schema", [])
        self.detailed_scores = scores.get("detailed_scores", {})

    def _get_expectation_language(self, expected_score: float, bucket_size: int) -> str:
        """Convert expected_score to human-readable JD expectation language."""
        if expected_score >= 0.95:
            return "Must know ALL skills in this bucket"
        elif expected_score >= 0.65:
            return "Preferred to have strong proficiency"
        elif bucket_size > 0 and expected_score < 1.0 / bucket_size:
            return f"Proficiency in ATLEAST ONE of {bucket_size} options"
        else:
            return f"Moderate proficiency expected (~{int(expected_score*100)}%)"
    
    def _format_score_context(self):
        """Converts scores to a readable context for the LLM, including bucket details, expectations, and sources."""
        lines = []
        
        # Build a bucket lookup for skill details
        bucket_lookup = {b.name: b for b in self.bucket_schema}
        
        # Calculate overall candidate alignment
        overall_candidate_score = sum(self.radar_data.values()) / len(self.radar_data) if self.radar_data else 0.0
        overall_jd_expectation = sum(self.jd_expectations.values()) / len(self.jd_expectations) if self.jd_expectations else 0.0
        
        # Add overall summary
        lines.append("=== OVERALL CANDIDATE ALIGNMENT ===")
        lines.append(f"Candidate Overall Score: {int(overall_candidate_score*100)}%")
        lines.append(f"JD Overall Expectation: {int(overall_jd_expectation*100)}%")
        lines.append(f"Overall Gap: {(overall_jd_expectation - overall_candidate_score):.2f}")
        lines.append("")
        lines.append("=== BUCKET-BY-BUCKET ANALYSIS ===")
        lines.append("")
        
        for bucket_name, candidate_score in self.radar_data.items():
            expected_score = self.jd_expectations.get(bucket_name, 1.0)
            sources = self.evidence_context.get(bucket_name, [])
            bucket_obj = bucket_lookup.get(bucket_name)
            
            # Determine status
            status = "STRONG" if candidate_score > 0.7 else "MODERATE" if candidate_score > 0.4 else "MISSING EVIDENCE"
            
            # Get expectation language
            bucket_size = len(bucket_obj.skills) if bucket_obj else 0
            expectation_language = self._get_expectation_language(expected_score, bucket_size)
            
            # Find which skills candidate has evidence for
            skills_with_evidence = []
            if bucket_obj:
                for skill in bucket_obj.skills:
                    if skill in self.detailed_scores and self.detailed_scores[skill] > 0:
                        skills_with_evidence.append(skill)
            
            # Include gap information
            gap = expected_score - candidate_score
            if gap > 0:
                gap_indicator = f" [GAP: {gap:.2f}]"
            else:
                gap_indicator = f" [EXCEEDS: {abs(gap):.2f}]"
            
            # Show all skills for context, but explain the expectation
            skill_list = f"\n   JD requires: {', '.join(bucket_obj.skills)}" if bucket_obj else ""
            
            # Format sources as evidence references
            sources_str = ""
            if sources:
                sources_str = f"\n   Sources: {'; '.join(sources)}"
            
            lines.append(f"- {bucket_name}: {status} (Candidate: {int(candidate_score*100)}% vs JD: {int(expected_score*100)}%){gap_indicator}")
            lines.append(f"   Expectation: {expectation_language}")
            lines.append(f"   Evidence: {', '.join(skills_with_evidence) if skills_with_evidence else 'No concrete evidence found'}{skill_list}{sources_str}")
            lines.append("")
        
        return "\n".join(lines)

    def generate_closure(self):
        """
        Generates the 'Ethical Gap Analysis' using the LLM.
        """
        context = self._format_score_context()
        
        prompt = auditor(context)
        response = self.client.chat.completions.create(
            model=settings.JD_SKILL_MODEL,
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0
        )
        return response.choices[0].message.content
