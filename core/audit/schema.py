from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field

class BucketItem(BaseModel):
    name: str = Field(..., description="Name of the bucket")
    skills: List[str] = Field(..., description="Array of skills that belong under the given bucket")
    # Literal enforces that the value must be exactly one of these two strings
    priority: Literal["CORE", "PREFERRED"] = Field(..., description="Priority level of the bucket")

class Buckets(BaseModel):
    model_config = ConfigDict(extra='forbid')
    buckets: List[BucketItem]