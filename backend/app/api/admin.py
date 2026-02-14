"""Admin API endpoints — rules, templates, patients, encounters."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.db.database import get_db
from app.schemas.admin import (
    RuleCreate, RuleResponse, RuleUpdate,
    CPGTemplateResponse, PatientResponse, EncounterDetailResponse,
)
from app.models.admin import Rule, CPGTemplate
from app.models.patient import Patient, Encounter, Diagnosis, Observation, OrderRecord, ProgressNote

router = APIRouter()


@router.get("/rules", response_model=list[RuleResponse])
async def list_rules(db: Session = Depends(get_db)) -> list[RuleResponse]:
    rules = db.query(Rule).all()
    return [RuleResponse.model_validate(r) for r in rules]


@router.post("/rules", response_model=RuleResponse)
async def create_rule(rule: RuleCreate, db: Session = Depends(get_db)) -> RuleResponse:
    db_rule = Rule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return RuleResponse.model_validate(db_rule)


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str, update: RuleUpdate, db: Session = Depends(get_db)) -> RuleResponse:
    db_rule = db.query(Rule).filter(Rule.rule_id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, val in update.model_dump(exclude_unset=True).items():
        setattr(db_rule, key, val)
    db.commit()
    db.refresh(db_rule)
    return RuleResponse.model_validate(db_rule)


@router.get("/templates", response_model=list[CPGTemplateResponse])
async def list_templates(db: Session = Depends(get_db)) -> list[CPGTemplateResponse]:
    templates = db.query(CPGTemplate).all()
    return [CPGTemplateResponse.model_validate(t) for t in templates]


@router.get("/patients", response_model=list[PatientResponse])
async def list_patients(db: Session = Depends(get_db)) -> list[PatientResponse]:
    patients = db.query(Patient).all()
    return [PatientResponse.model_validate(p) for p in patients]


@router.get("/patients/{patient_id}/encounters")
async def patient_encounters(patient_id: int, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    encounters = db.query(Encounter).filter(Encounter.patient_id == patient_id).all()
    result = []
    for enc in encounters:
        result.append({
            "id": enc.id,
            "encounter_id": enc.encounter_id,
            "admit_date": str(enc.admit_date),
            "ward": enc.ward,
            "status": enc.status,
            "chief_complaint": enc.chief_complaint,
        })
    return result


@router.get("/encounters/{encounter_id}", response_model=EncounterDetailResponse)
async def get_encounter(encounter_id: str, db: Session = Depends(get_db)) -> EncounterDetailResponse:
    enc = db.query(Encounter).filter(Encounter.encounter_id == encounter_id).first()
    if not enc:
        raise HTTPException(status_code=404, detail="Encounter not found")

    patient = db.query(Patient).filter(Patient.id == enc.patient_id).first()

    return EncounterDetailResponse(
        id=enc.id,
        encounter_id=enc.encounter_id,
        patient_id=enc.patient_id,
        admit_date=str(enc.admit_date),
        dc_date=str(enc.dc_date) if enc.dc_date else None,
        ward=enc.ward,
        los=enc.los,
        status=enc.status,
        chief_complaint=enc.chief_complaint,
        patient=PatientResponse.model_validate(patient),
        diagnoses=[
            {"id": d.id, "icd_code": d.icd_code, "description": d.description, "dx_type": d.dx_type, "source": d.source, "confidence": d.confidence}
            for d in db.query(Diagnosis).filter(Diagnosis.encounter_id == enc.id).all()
        ],
        observations=[
            {"id": o.id, "obs_type": o.obs_type, "code": o.code, "display_name": o.display_name, "value": o.value, "unit": o.unit, "abnormal_flag": o.abnormal_flag}
            for o in db.query(Observation).filter(Observation.encounter_id == enc.id).all()
        ],
        orders=[
            {"id": o.id, "category": o.category, "standard_code": o.standard_code, "display_name": o.display_name, "status": o.status}
            for o in db.query(OrderRecord).filter(OrderRecord.encounter_id == enc.id).all()
        ],
        progress_notes=[
            {"id": n.id, "date_time": str(n.date_time), "text": n.text, "author": n.author}
            for n in db.query(ProgressNote).filter(ProgressNote.encounter_id == enc.id).all()
        ],
    )
