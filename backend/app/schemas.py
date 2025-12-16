from pydantic import BaseModel
from typing import List, Optional, Any

class RankRequest(BaseModel):
    job_description: str
    top_k: Optional[int] = 10
    skill_vs_exp_weight: Optional[float] = 0.5

class Evidence(BaseModel):
    text: str
    file: str
    page: Optional[int] = None

class CandidateResult(BaseModel):
    candidate_id: str
    name: Optional[str]
    overall_score: float
    skill_match_score: float
    experience_score: float
    matched_skills: List[Any]
    demonstrated_experiences: List[Any]
    provenance: Any
    explainability: Optional[str]

class RankResponse(BaseModel):
    job_id: str
    results: List[CandidateResult]
