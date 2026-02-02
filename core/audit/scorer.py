import re
import json
from core.audit.schema import Buckets
from config import settings
from config.utils import load_jd
from config.prompts import jd_bucketing
from groq import Groq

class Scorer:
    """
    Implements the 'Grounded Auditor' scoring logic.
    1. Taxonomy Grouping (Buckets)
    2. Atomic Scoring (Evidence Density)
    3. Grouped Competency (Max Polling)
    """
    

    def __init__(self, chunks, jd_skills, jd_text):
        """
        :param chunks: List of chunk objects from AgenticChunker
        :param jd_skills: List of skills extracted from JD
        """
        self.chunks = chunks
        self.jd=load_jd(jd_text)
        self.client = Groq(api_key=settings.API_KEY)
        self.jd_skills = [s.lower() for s in jd_skills]
        self.skill_map = self._map_chunks_to_skills()
        self._get_bucket(None)  # Initialize bucket schema from JD skills

    def _map_chunks_to_skills(self):
        """Maps skill names to their chunks for easy access."""
        mapping = {}
        for chunk in self.chunks:
            skill = chunk.get('focus_skill', '').lower()
            if skill:
                 mapping[skill] = chunk
        return mapping

    def _get_bucket(self, skill=None):
        """Initialize buckets from JD skills via LLM (skill param unused, kept for API compat)."""
        prompt = jd_bucketing(self.jd, self.jd_skills) 
        
        response = self.client.chat.completions.create(
            model=settings.CHUNKER_MODEL,
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_analysis",
                    "strict": True,
                    "schema": Buckets.model_json_schema()
                }
            }
        )
        
        # Parse the raw JSON string
        raw_content = json.loads(response.choices[0].message.content)
        
        # Validate it against your Pydantic model to ensure priority is CORE/PREFERRED
        validated_data = Buckets.model_validate(raw_content)
        
        # Assign the list of bucket items to self.bucket_schema
        self.bucket_schema = validated_data.buckets

    def calculate_atomic_score(self, skill_name):
        """
        Step 1: Atomic Score based on Evidence Density.
        Formula: min(1.0, (claim_count * 0.3) + (0.2 if implementation_evidence))
        """
        chunk = self.skill_map.get(skill_name)
        if not chunk or not chunk.get('claims'):
            return 0.0, []
        
        claims = chunk.get('claims', [])
        sources=[]
        claim_count = len(claims)

        # Priority Logic: Professional Experience > Projects > Skills
        weight = 0.0
        for c in claims:
            text = c.get('claim_text', '').lower()
            section = c.get('source_section', '').lower()
            
            # Identify the "Pedigree" of the claim
            if "experience" in section or "intern" in section:
                weight += 0.5  # Heavy weight for professional work
                sources.append(f"Work Experience at {section.split(':')[-1].strip()}")
            elif "project" in section:
                weight += 0.3  # Moderate weight for projects
                sources.append(f"Project: {text[:30]}...")
            else:
                weight += 0.1  # Low weight for simple skill mentions

        # Implementation Bonus
        has_impl = any(re.search(r'\b(built|implemented|deployed|architected|designed)\b', 
                                 c.get('claim_text', '').lower()) for c in claims)
        
        final_atomic = min(1.0, weight + (0.2 if has_impl else 0.0))
        return final_atomic, list(set(sources)) # Return score and source context
    
    def compute_scores(self):
        """
        Step 2: Aggregation (Max Pooling per Bucket).
        Returns:
            - radar_data: Dict[Category, Score] - Candidate's actual scores
            - jd_expectations: Dict[Category, Score] - JD baseline expectations
            - evidence_context: Dict[Category, Sources] - Evidence traces
        """
        detailed_scores = {}
        radar_data = {}
        jd_expectations = {}
        evidence_context = {}
        core_scores = []
        pref_scores = []

        for bucket in self.bucket_schema:
            # We iterate through the LLM-defined buckets directly.
            best_score = 0.0
            best_sources=[]

            for skill in bucket.skills:
                score, sources = self.calculate_atomic_score(skill)
                detailed_scores[skill] = score
                if score > best_score:
                    best_score = score
                    best_sources = sources
            
            radar_data[bucket.name] = best_score
            # JD expectation: From LLM analysis of actual JD language
            jd_expectations[bucket.name] = bucket.expected_score
            evidence_context[bucket.name] = best_sources
            
            # Separate scores for weighted final calculation.
            if bucket.priority == "CORE":
                core_scores.append(best_score)
            else:
                pref_scores.append(best_score)

        avg_core = sum(core_scores) / len(core_scores) if core_scores else 0.0
        avg_pref = sum(pref_scores) / len(pref_scores) if pref_scores else 0.0
        
        # Ethical weighting: 80% Core / 20% Preferred.
        final_score = (avg_core * 0.8) + (avg_pref * 0.2)

        return {
            "final_score": round(final_score, 2),
            "radar_data": radar_data,
            "jd_expectations": jd_expectations,
            "evidence_context": evidence_context,
            "bucket_schema": self.bucket_schema,  # Pass bucket definitions for detailed explanations
            "detailed_scores": detailed_scores,  # Pass all skill scores
            "core_alignment": avg_core
        }
