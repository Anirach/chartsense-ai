"""Code Suggestion API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.coding import CodeSuggestionResponse, CodeSuggestionItem, AcceptCodesRequest
from app.services.drg import get_code_suggestions, calculate_rw
from app.models.patient import Encounter, Diagnosis, Observation, OrderRecord, ProgressNote

router = APIRouter()


def _build_encounter_data(encounter_id: str, db: Session) -> dict:
    enc = db.query(Encounter).filter(Encounter.encounter_id == encounter_id).first()
    if not enc:
        return _demo_data(encounter_id)

    return {
        "diagnoses": [
            {"icd_code": d.icd_code, "dx_type": d.dx_type}
            for d in db.query(Diagnosis).filter(Diagnosis.encounter_id == enc.id).all()
        ],
        "observations": [
            {"obs_type": o.obs_type, "code": o.code, "value": o.value}
            for o in db.query(Observation).filter(Observation.encounter_id == enc.id).all()
        ],
        "orders": [
            {"category": o.category, "standard_code": o.standard_code}
            for o in db.query(OrderRecord).filter(OrderRecord.encounter_id == enc.id).all()
        ],
        "progress_notes": [
            {"text": n.text}
            for n in db.query(ProgressNote).filter(ProgressNote.encounter_id == enc.id).all()
        ],
    }


@router.post("/{encounter_id}", response_model=CodeSuggestionResponse)
async def get_suggestions(encounter_id: str, db: Session = Depends(get_db)) -> CodeSuggestionResponse:
    data = _build_encounter_data(encounter_id, db)
    suggestions = get_code_suggestions(data)
    current_codes = [d["icd_code"] for d in data.get("diagnoses", [])]
    suggested_codes = [s["icd_code"] for s in suggestions]
    rw = calculate_rw(current_codes, suggested_codes)

    items = [
        CodeSuggestionItem(id=i + 1, **s)
        for i, s in enumerate(suggestions)
    ]

    return CodeSuggestionResponse(
        encounter_id=encounter_id,
        suggestions=items,
        rw_before=rw["rw_before"],
        rw_after=rw["rw_after"],
        rw_delta=rw["delta"],
        revenue_impact_thb=rw["revenue_impact_thb"],
    )


@router.post("/{encounter_id}/accept")
async def accept_codes(encounter_id: str, req: AcceptCodesRequest) -> dict:
    return {
        "status": "success",
        "encounter_id": encounter_id,
        "accepted_ids": req.suggestion_ids,
        "message": f"รับรหัส {len(req.suggestion_ids)} รายการเรียบร้อย",
    }


def _demo_data(encounter_id: str) -> dict:
    return {
        "diagnoses": [{"icd_code": "J18.9", "dx_type": "PDx"}],
        "observations": [
            {"obs_type": "lab", "code": "Creatinine", "value": "1.8"},
            {"obs_type": "lab", "code": "FBS", "value": "180"},
            {"obs_type": "lab", "code": "Hemoglobin", "value": "9.5"},
            {"obs_type": "lab", "code": "Potassium", "value": "3.2"},
            {"obs_type": "lab", "code": "Procalcitonin", "value": "3.5"},
        ],
        "orders": [{"category": "MEDICATION", "standard_code": "Ceftriaxone"}],
        "progress_notes": [{"text": "ผู้ป่วยมีไข้ ไอมีเสมหะ เหนื่อยหอบ"}],
    }
