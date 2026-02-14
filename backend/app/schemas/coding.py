from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CodeSuggestionItem(BaseModel):
    id: int
    icd_code: str
    description: str
    dx_type: str
    confidence: float
    evidence: list[str]
    rw_impact: float
    status: str


class CodeSuggestionResponse(BaseModel):
    encounter_id: str
    suggestions: list[CodeSuggestionItem]
    rw_before: float
    rw_after: float
    rw_delta: float
    revenue_impact_thb: float
    drg: Optional[str] = None


class AcceptCodesRequest(BaseModel):
    suggestion_ids: list[int]
