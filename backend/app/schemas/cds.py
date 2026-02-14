from pydantic import BaseModel
from typing import Optional


class VitalSigns(BaseModel):
    temperature: Optional[float] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    spo2: Optional[float] = None
    gcs: Optional[int] = None


class LabResult(BaseModel):
    code: str
    value: float
    unit: str


class PreDiagnosisRequest(BaseModel):
    symptoms: list[str]
    vitals: Optional[VitalSigns] = None
    labs: list[LabResult] = []
    pmh: list[str] = []
    age: int = 60
    sex: str = "M"
    chief_complaint: Optional[str] = None


class DifferentialDiagnosis(BaseModel):
    rank: int
    icd_code: str
    description: str
    description_th: str
    probability: float
    reasoning: str
    evidence: list[str]
    cpg_reference: Optional[str] = None


class PreDiagnosisResponse(BaseModel):
    differentials: list[DifferentialDiagnosis]
    primary_disease_group: str
    confidence_note: str


class OrderItem(BaseModel):
    category: str
    code: str
    display_name: str
    priority: str
    rationale: str
    cpg_source: Optional[str] = None


class OrderSuggestionRequest(BaseModel):
    encounter_id: Optional[str] = None
    primary_dx: str
    icd_code: str
    age: int = 60
    sex: str = "M"
    comorbidities: list[str] = []
    creatinine: Optional[float] = None
    gfr: Optional[float] = None


class OrderSuggestionResponse(BaseModel):
    orders: list[OrderItem]
    disease_group: str
    personalization_notes: list[str]


class AdmissionDecisionRequest(BaseModel):
    encounter_id: Optional[str] = None
    primary_dx: str
    icd_code: str
    vitals: VitalSigns
    labs: list[LabResult] = []
    age: int = 60
    confusion: bool = False
    urea: Optional[float] = None
    nursing_home: bool = False


class RiskScoreDetail(BaseModel):
    tool_name: str
    score: int
    max_score: int
    components: dict[str, int]
    interpretation: str
    mortality_risk: Optional[str] = None


class AdmissionDecisionResponse(BaseModel):
    recommendation: str
    risk_level: str
    risk_scores: list[RiskScoreDetail]
    reasoning: str
    suggested_ward: str
