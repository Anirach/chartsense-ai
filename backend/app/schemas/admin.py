from pydantic import BaseModel
from typing import Optional, Any


class RuleCreate(BaseModel):
    rule_id: str
    category: str
    name: str
    description: Optional[str] = None
    weight: float = 1.0
    condition: dict[str, Any]
    active: bool = True


class RuleResponse(BaseModel):
    id: int
    rule_id: str
    category: str
    name: str
    description: Optional[str] = None
    weight: float
    condition: dict[str, Any]
    active: bool

    class Config:
        from_attributes = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    condition: Optional[dict[str, Any]] = None
    active: Optional[bool] = None


class CPGTemplateResponse(BaseModel):
    id: int
    template_id: str
    disease_group: str
    name: str
    description: Optional[str] = None
    orders: list[dict[str, Any]]
    criteria: dict[str, Any]
    version: str

    class Config:
        from_attributes = True


class PatientResponse(BaseModel):
    id: int
    hn: str
    name: str
    age: int
    sex: str
    pmh: list[str]
    allergies: list[str]

    class Config:
        from_attributes = True


class EncounterResponse(BaseModel):
    id: int
    encounter_id: str
    patient_id: int
    admit_date: str
    dc_date: Optional[str] = None
    ward: str
    los: int
    status: str
    chief_complaint: Optional[str] = None

    class Config:
        from_attributes = True


class EncounterDetailResponse(EncounterResponse):
    patient: PatientResponse
    diagnoses: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    orders: list[dict[str, Any]] = []
    progress_notes: list[dict[str, Any]] = []
