'''
schema.py: Store pydantic models to fit the JSON schema
- only include JSON schema / dataclasses
'''
from typing import List, Optional
from pydantic import BaseModel

class Metadata(BaseModel):
    parsed_at:str
    parser_version: str
    
class Education(BaseModel):
    degree: str
    institution: str
    duration: str
    score: Optional[str] = None

class Skills(BaseModel):
    languages: List[str] = []
    frameworks: List[str] = []
    tools: List[str] = []

class Experience(BaseModel):
    role: str
    company: str
    duration: str
    claims: List[str]
    tools: List[str] = []

class Project(BaseModel):
    name: str
    claims: List[str]
    tools: List[str] = []

class Resume(BaseModel):
    resume_id:str
    metadata: Metadata
    education: List[Education] = []
    skills: Skills
    experience: List[Experience] = []
    projects: List[Project] = []
