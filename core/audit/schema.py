from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field

class BucketItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(..., description="Name of the bucket")
    skills: List[str] = Field(..., description="Array of skills that belong under the given bucket")
    # Literal enforces that the value must be exactly one of these two strings
    priority: Literal["CORE", "PREFERRED"] = Field(..., description="Priority level of the bucket")
    expected_score: float = Field(..., description="Expected proficiency score (0.0-1.0) based on JD requirements. E.g., 'at least one': 0.2, 'must master all': 1.0, 'preferred': 0.7")

class Buckets(BaseModel):
    model_config = ConfigDict(extra='forbid')
    buckets: List[BucketItem]