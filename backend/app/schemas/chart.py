from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChartGap(BaseModel):
    rule_id: str
    category: str
    description: str
    severity: str
    suggested_action: Optional[str] = None
    suggested_code: Optional[str] = None


class CategoryBreakdown(BaseModel):
    category: str
    score: float
    max_score: float
    weight: float
    items_found: int
    items_expected: int


class ChartScoreResponse(BaseModel):
    encounter_id: str
    total_score: float
    grade: str
    breakdown: list[CategoryBreakdown]
    gaps: list[ChartGap]
    evaluated_at: datetime


class EvaluateChartRequest(BaseModel):
    encounter_id: str
    force_refresh: bool = False
