"""Chart Completeness API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.schemas.chart import ChartScoreResponse, EvaluateChartRequest, ChartGap, CategoryBreakdown
from app.services.rules import evaluate_chart
from app.models.patient import Encounter, Diagnosis, Observation, OrderRecord, ProgressNote

router = APIRouter()


def _get_encounter_data(encounter_id: str, db: Session) -> dict:
    enc = db.query(Encounter).filter(Encounter.encounter_id == encounter_id).first()
    if not enc:
        return {}

    return {
        "encounter_id": enc.encounter_id,
        "status": enc.status,
        "diagnoses": [
            {"icd_code": d.icd_code, "dx_type": d.dx_type, "description": d.description}
            for d in db.query(Diagnosis).filter(Diagnosis.encounter_id == enc.id).all()
        ],
        "observations": [
            {"obs_type": o.obs_type, "code": o.code, "value": o.value, "abnormal_flag": o.abnormal_flag}
            for o in db.query(Observation).filter(Observation.encounter_id == enc.id).all()
        ],
        "orders": [
            {"category": o.category, "standard_code": o.standard_code, "display_name": o.display_name}
            for o in db.query(OrderRecord).filter(OrderRecord.encounter_id == enc.id).all()
        ],
        "progress_notes": [
            {"date_time": str(n.date_time), "text": n.text}
            for n in db.query(ProgressNote).filter(ProgressNote.encounter_id == enc.id).all()
        ],
    }


@router.get("/{encounter_id}", response_model=ChartScoreResponse)
async def get_chart_score(encounter_id: str, db: Session = Depends(get_db)) -> ChartScoreResponse:
    data = _get_encounter_data(encounter_id, db)
    if not data:
        # Return demo data
        data = _demo_encounter_data(encounter_id)

    result = evaluate_chart(data)

    return ChartScoreResponse(
        encounter_id=encounter_id,
        total_score=result["total_score"],
        grade=result["grade"],
        breakdown=[CategoryBreakdown(**b) for b in result["breakdown"]],
        gaps=[ChartGap(**g) for g in result["gaps"]],
        evaluated_at=datetime.utcnow(),
    )


@router.post("/evaluate", response_model=ChartScoreResponse)
async def evaluate(req: EvaluateChartRequest, db: Session = Depends(get_db)) -> ChartScoreResponse:
    data = _get_encounter_data(req.encounter_id, db)
    if not data:
        data = _demo_encounter_data(req.encounter_id)

    result = evaluate_chart(data)

    return ChartScoreResponse(
        encounter_id=req.encounter_id,
        total_score=result["total_score"],
        grade=result["grade"],
        breakdown=[CategoryBreakdown(**b) for b in result["breakdown"]],
        gaps=[ChartGap(**g) for g in result["gaps"]],
        evaluated_at=datetime.utcnow(),
    )


def _demo_encounter_data(encounter_id: str) -> dict:
    """Return demo data for testing."""
    return {
        "encounter_id": encounter_id,
        "status": "ACTIVE",
        "diagnoses": [
            {"icd_code": "J18.9", "dx_type": "PDx", "description": "Pneumonia"},
        ],
        "observations": [
            {"obs_type": "vital", "code": "temperature", "value": "38.5", "abnormal_flag": True},
            {"obs_type": "vital", "code": "heart_rate", "value": "98", "abnormal_flag": False},
            {"obs_type": "vital", "code": "respiratory_rate", "value": "24", "abnormal_flag": True},
            {"obs_type": "vital", "code": "systolic_bp", "value": "150", "abnormal_flag": True},
            {"obs_type": "lab", "code": "Creatinine", "value": "1.8", "abnormal_flag": True},
            {"obs_type": "lab", "code": "FBS", "value": "180", "abnormal_flag": True},
            {"obs_type": "lab", "code": "Hemoglobin", "value": "9.5", "abnormal_flag": True},
        ],
        "orders": [
            {"category": "MEDICATION", "standard_code": "Ceftriaxone", "display_name": "Ceftriaxone 2g IV"},
        ],
        "progress_notes": [
            {"date_time": "2026-02-14T08:00:00", "text": "ผู้ป่วยยังมีไข้ ไอมีเสมหะ"},
        ],
    }
