from typing import List
from pydantic import BaseModel, Field, ConfigDict

class RelevanceAnalysis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    score: int = Field(..., description="Relevance score from 1-10")
    reasoning: str = Field(..., description="Explanation of why this claim connects to the skill")

class Claim(BaseModel):
    model_config = ConfigDict(extra='forbid')
    claim_text: str = Field(..., description="Verbatim text from resume")
    source_section: str = Field(..., description="Section origin like 'Project: X' or 'Experience: Y'")
    relevance_analysis: RelevanceAnalysis

class ResumeChunk(BaseModel):
    model_config = ConfigDict(extra='forbid')
    focus_skill: str = Field(..., description="The target skill this chunk aggregates evidence for")
    chunk_summary: str = Field(..., description="1-2 sentence summary of candidate's proficiency")
    claims: List[Claim]

class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chunks: List[ResumeChunk]