'''
chunker.py: Contains the AgenticChunking class, which chunks resume data based on skills required by the JD 
'''

import json
import uuid
from typing import List, Dict, Any
from groq import Groq
from core.chunker.schema import ResumeAnalysis
from config.settings import API_KEY, CHUNKER_MODEL
from config.prompts import chunker_prompt
from config.utils import load_jd, load_jd_from_dir, load_parsed_resume
from core.chunker.skill_extractor import JDSkillExtractor


def store_chunks_to_json(chunks: list, output_path: str = "data/stored_chunks.json"):
    """Store unstripped chunks to JSON for traceability"""
    with open(output_path, 'w') as f:
        json.dump(chunks, f, indent=2)
    print(f"✓ Chunks stored to {output_path}")

class AgenticChunker:
    def __init__(self, resume_parsed=Dict[str, Any]):
        self.resume=resume_parsed
        self.client=Groq(api_key=API_KEY)
    
    def _generate_chunk_id(self, skill: str) -> str:
        """ 
        Create a deterministic but unique ID for eveyr chunk
        """ 
        clean_skill = skill.lower().replace(" ", "_")
        unique_suffix = str(uuid.uuid4())[:8]
        return f"chunk_{clean_skill}_{unique_suffix}"
    

    def chunk_by_skills(self):
        resume=self.resume

        try:
            # try accessing JD from streamlit session
            jd=load_jd()
        except:
            # fallback, read the saved text file
            jd=load_jd_from_dir()
        
        target_skills=JDSkillExtractor().extract_skills(jd)
        prompt=chunker_prompt(target_skills, resume)

        response = self.client.chat.completions.create(
            model=CHUNKER_MODEL,
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_analysis",
                    "strict": True,
                    "schema": ResumeAnalysis.model_json_schema()
                }
            }
        )

        try:
            # Parse response into Pydantic Model
            content = json.loads(response.choices[0].message.content)
            analysis = ResumeAnalysis.model_validate(content)
            
            # Convert to list of dicts to add metadata
            response_json = [chunk.model_dump() for chunk in analysis.chunks]
            
            # Add metadata (ID)
            for chunk in response_json:
                chunk['chunk_id'] = self._generate_chunk_id(chunk['focus_skill'])
            
            # Store chunks to JSON for traceability
            store_chunks_to_json(response_json)
                
            return response_json
            
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            return []
        
if __name__=="__main__":
    resume_parsed=load_parsed_resume()
    chunker=AgenticChunker(resume_parsed)
    print(chunker.chunk_by_skills())