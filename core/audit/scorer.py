import re

class Scorer:
    """
    Implements the 'Grounded Auditor' scoring logic.
    1. Taxonomy Grouping (Buckets)
    2. Atomic Scoring (Evidence Density)
    3. Grouped Competency (Max Polling)
    """
    
    # Static Taxonomy Fallback (Can be enhanced with LLM later)
    # Static Taxonomy Fallback (Can be enhanced with LLM later)
    TAXONOMY = {
        "Languages": ["python", "java", "c++", "c#", "javascript", "typescript", "go", "ruby", "php", "rust", "swift", "kotlin", "scala"],
        "Backend": ["django", "flask", "fastapi", "spring", "nodejs", "express", "rails", "graphql", "rest", "grpc"],
        "Frontend": ["react", "vue", "angular", "html", "css", "tailwind", "bootstrap", "redux", "jquery", "nextjs"],
        "Fullstack": ["mern", "mean", "jamstack"],
        "Cloud/DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "circleci", "github actions", "linux", "bash", "nginx"],
        "Data Engineering": ["sql", "postgres", "mysql", "mongodb", "redis", "cassandra", "elasticsearch", "spark", "kafka", "hadoop", "airflow", "snowflake", "bigquery"],
        "AI/ML": ["pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "transformers", "huggingface", "llm", "rag", "opencv", "nltk", "spacy"],
        "Mobile": ["react native", "flutter", "ios", "android", "swift", "kotlin"],
        "Testing/QA": ["selenium", "pytest", "junit", "mocha", "jest", "cypress", "playwright"],
        "System Design": ["microservices", "distributed systems", "system design", "scalability", "load balancing", "caching", "database design"],
        "General": [] 
    }

    def __init__(self, chunks, jd_skills):
        """
        :param chunks: List of chunk objects from AgenticChunker
        :param jd_skills: List of skills extracted from JD
        """
        self.chunks = chunks
        self.jd_skills = [s.lower() for s in jd_skills]
        self.skill_map = self._map_chunks_to_skills()

    def _map_chunks_to_skills(self):
        """Maps skill names to their chunks for easy access."""
        mapping = {}
        for chunk in self.chunks:
            skill = chunk.get('focus_skill', '').lower()
            if skill:
                 mapping[skill] = chunk
        return mapping

    def _get_bucket(self, skill):
        """Finds the bucket a skill belongs to."""
        for category, skills in self.TAXONOMY.items():
            if any(s in skill for s in skills): # Substring match for robustness
                return category
        return "General"

    def calculate_atomic_score(self, skill_name):
        """
        Step 1: Atomic Score based on Evidence Density.
        Formula: min(1.0, (claim_count * 0.3) + (0.2 if implementation_evidence))
        """
        chunk = self.skill_map.get(skill_name)
        if not chunk:
            return 0.0
        
        claims = chunk.get('claims', [])
        claim_count = len(claims)
        if claim_count == 0:
            return 0.0

        # Check for strong evidence keywords
        has_implementation = any(
            re.search(r'\b(built|implemented|deployed|architected|designed)\b', c.get('claim_text', '').lower()) 
            for c in claims
        )
        
        base_score = claim_count * 0.3
        bonus = 0.2 if has_implementation else 0.0
        
        return min(1.0, base_score + bonus)

    def compute_scores(self):
        """
        Step 2: Aggregation (Max Pooling per Bucket).
        Returns:
            - radar_data: Dict[Category, Score]
            - detailed_scores: Diet[Skill, Score]
        """
        detailed_scores = {}
        bucket_scores = {k: 0.0 for k in self.TAXONOMY.keys()}
        bucket_scores["General"] = 0.0 # Ensure exists

        # Calculate atomic scores for all JD skills
        for skill in self.jd_skills:
            score = self.calculate_atomic_score(skill)
            detailed_scores[skill] = score
            
            # Max Pooling Logic
            bucket = self._get_bucket(skill)
            if score > bucket_scores.get(bucket, 0.0):
                bucket_scores[bucket] = score
        
        # Filter out empty buckets for the Radar Chart to look clean
        final_buckets = {k: v for k, v in bucket_scores.items() if v > 0 or k in ["Languages", "Backend"]} 
        
        return {
            "radar_data": final_buckets,
            "detailed_scores": detailed_scores
        }
