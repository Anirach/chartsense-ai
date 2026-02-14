"""Clinical Decision Support API endpoints."""

from fastapi import APIRouter
from app.schemas.cds import (
    PreDiagnosisRequest, PreDiagnosisResponse, DifferentialDiagnosis,
    OrderSuggestionRequest, OrderSuggestionResponse, OrderItem,
    AdmissionDecisionRequest, AdmissionDecisionResponse, RiskScoreDetail,
)
from app.services.graphrag import find_differential_diagnoses, KNOWLEDGE_GRAPH

router = APIRouter()

# CPG-based order templates
ORDER_TEMPLATES: dict[str, list[dict]] = {
    "CAP": [
        {"category": "LAB", "code": "CBC", "display_name": "Complete Blood Count", "priority": "ESSENTIAL", "rationale": "ประเมินการติดเชื้อ (WBC, Neutrophil)"},
        {"category": "LAB", "code": "BUN_Cr", "display_name": "BUN/Creatinine", "priority": "ESSENTIAL", "rationale": "ประเมินไต (CURB-65 component)"},
        {"category": "LAB", "code": "Electrolytes", "display_name": "Na/K/Cl/CO2", "priority": "ESSENTIAL", "rationale": "ประเมิน electrolyte imbalance"},
        {"category": "LAB", "code": "Blood_culture", "display_name": "Blood Culture x2", "priority": "ESSENTIAL", "rationale": "หา causative organism (ก่อนให้ ATB)"},
        {"category": "LAB", "code": "Sputum_culture", "display_name": "Sputum Culture & Gram Stain", "priority": "RECOMMENDED", "rationale": "ระบุเชื้อก่อโรค"},
        {"category": "LAB", "code": "Procalcitonin", "display_name": "Procalcitonin", "priority": "RECOMMENDED", "rationale": "แยก bacterial vs viral, ติดตาม ATB response"},
        {"category": "IMAGING", "code": "CXR_PA", "display_name": "Chest X-ray PA upright", "priority": "ESSENTIAL", "rationale": "ยืนยัน infiltrate, ประเมิน severity"},
        {"category": "MEDICATION", "code": "Ceftriaxone", "display_name": "Ceftriaxone 2g IV q24h", "priority": "ESSENTIAL", "rationale": "Empiric ATB สำหรับ CAP (Thai CPG 2023)", "cpg_source": "Thai CPG CAP 2023"},
        {"category": "MEDICATION", "code": "Azithromycin", "display_name": "Azithromycin 500mg IV/PO qd", "priority": "ESSENTIAL", "rationale": "Atypical coverage (Thai CPG 2023)", "cpg_source": "Thai CPG CAP 2023"},
        {"category": "MEDICATION", "code": "Paracetamol", "display_name": "Paracetamol 500mg PO q6h PRN", "priority": "RECOMMENDED", "rationale": "ลดไข้"},
        {"category": "NURSING", "code": "O2_monitor", "display_name": "SpO2 monitoring q4h", "priority": "ESSENTIAL", "rationale": "เฝ้าระวัง respiratory failure"},
        {"category": "NURSING", "code": "I_O", "display_name": "Intake/Output monitoring", "priority": "RECOMMENDED", "rationale": "ประเมิน fluid balance"},
        {"category": "DIET", "code": "soft_diet", "display_name": "อาหารอ่อน (Soft diet)", "priority": "RECOMMENDED", "rationale": "ง่ายต่อการรับประทาน"},
    ],
    "DM": [
        {"category": "LAB", "code": "FBS", "display_name": "Fasting Blood Sugar", "priority": "ESSENTIAL", "rationale": "ประเมินระดับน้ำตาล"},
        {"category": "LAB", "code": "HbA1c", "display_name": "HbA1c", "priority": "ESSENTIAL", "rationale": "ประเมินการควบคุมเบาหวาน 3 เดือน"},
        {"category": "LAB", "code": "BUN_Cr", "display_name": "BUN/Creatinine", "priority": "ESSENTIAL", "rationale": "ประเมิน diabetic nephropathy"},
        {"category": "LAB", "code": "Electrolytes", "display_name": "Na/K/Cl/CO2", "priority": "ESSENTIAL", "rationale": "ประเมิน DKA/HHS"},
        {"category": "LAB", "code": "UA", "display_name": "Urinalysis", "priority": "ESSENTIAL", "rationale": "ดู ketone, protein"},
        {"category": "LAB", "code": "Lipid", "display_name": "Lipid Profile", "priority": "RECOMMENDED", "rationale": "ประเมิน cardiovascular risk"},
        {"category": "LAB", "code": "Urine_albumin", "display_name": "Urine Albumin/Creatinine Ratio", "priority": "RECOMMENDED", "rationale": "ตรวจ microalbuminuria"},
        {"category": "IMAGING", "code": "CXR", "display_name": "Chest X-ray", "priority": "OPTIONAL", "rationale": "ประเมินหัวใจและปอด"},
        {"category": "MEDICATION", "code": "Insulin_RI", "display_name": "Regular Insulin sliding scale", "priority": "ESSENTIAL", "rationale": "ควบคุมน้ำตาลขณะ admit"},
        {"category": "MEDICATION", "code": "NSS", "display_name": "NSS 1000ml IV 100ml/hr", "priority": "ESSENTIAL", "rationale": "แก้ไขภาวะขาดน้ำ"},
        {"category": "NURSING", "code": "DTX_q6h", "display_name": "DTX monitoring q6h", "priority": "ESSENTIAL", "rationale": "ติดตามระดับน้ำตาล"},
        {"category": "DIET", "code": "DM_diet", "display_name": "อาหารเบาหวาน 1500 kcal", "priority": "ESSENTIAL", "rationale": "ควบคุมน้ำตาลจากอาหาร"},
    ],
    "HF": [
        {"category": "LAB", "code": "BNP", "display_name": "BNP / NT-proBNP", "priority": "ESSENTIAL", "rationale": "ยืนยันและประเมิน severity ของ HF"},
        {"category": "LAB", "code": "CBC", "display_name": "Complete Blood Count", "priority": "ESSENTIAL", "rationale": "ประเมิน anemia (trigger factor)"},
        {"category": "LAB", "code": "BUN_Cr", "display_name": "BUN/Creatinine", "priority": "ESSENTIAL", "rationale": "ประเมิน cardiorenal syndrome"},
        {"category": "LAB", "code": "Electrolytes", "display_name": "Na/K/Cl/CO2", "priority": "ESSENTIAL", "rationale": "ประเมินก่อนให้ diuretics"},
        {"category": "LAB", "code": "Troponin", "display_name": "Troponin-T hs", "priority": "RECOMMENDED", "rationale": "ตรวจ acute coronary syndrome"},
        {"category": "LAB", "code": "TSH", "display_name": "Thyroid Function Test", "priority": "RECOMMENDED", "rationale": "แยก thyroid-related HF"},
        {"category": "IMAGING", "code": "CXR", "display_name": "Chest X-ray PA upright", "priority": "ESSENTIAL", "rationale": "ดู pulmonary congestion, cardiomegaly"},
        {"category": "IMAGING", "code": "Echo", "display_name": "Echocardiogram", "priority": "ESSENTIAL", "rationale": "ประเมิน EF, valvular disease, wall motion"},
        {"category": "IMAGING", "code": "ECG", "display_name": "12-Lead ECG", "priority": "ESSENTIAL", "rationale": "ดู arrhythmia, ischemia, LVH"},
        {"category": "MEDICATION", "code": "Furosemide", "display_name": "Furosemide 40mg IV", "priority": "ESSENTIAL", "rationale": "ลด fluid overload", "cpg_source": "ESC HF Guidelines 2023"},
        {"category": "MEDICATION", "code": "Enalapril", "display_name": "Enalapril 5mg PO BID", "priority": "ESSENTIAL", "rationale": "ACEi for HFrEF (EF<40%)", "cpg_source": "ESC HF Guidelines 2023"},
        {"category": "MEDICATION", "code": "Carvedilol", "display_name": "Carvedilol 3.125mg PO BID", "priority": "RECOMMENDED", "rationale": "Beta-blocker for HFrEF", "cpg_source": "ESC HF Guidelines 2023"},
        {"category": "NURSING", "code": "daily_weight", "display_name": "ชั่งน้ำหนักทุกเช้า", "priority": "ESSENTIAL", "rationale": "ติดตาม fluid balance"},
        {"category": "NURSING", "code": "fluid_restrict", "display_name": "จำกัดน้ำ 1500ml/วัน", "priority": "ESSENTIAL", "rationale": "ลด fluid overload"},
        {"category": "DIET", "code": "low_salt", "display_name": "อาหารจำกัดเกลือ <2g Na/วัน", "priority": "ESSENTIAL", "rationale": "ลด fluid retention"},
    ],
}


@router.post("/pre-diagnosis", response_model=PreDiagnosisResponse)
async def pre_diagnosis(req: PreDiagnosisRequest) -> PreDiagnosisResponse:
    labs = [{"code": l.code, "value": l.value, "unit": l.unit} for l in req.labs]
    results = find_differential_diagnoses(req.symptoms, req.age, req.sex, req.pmh, labs)

    differentials = []
    for i, r in enumerate(results):
        group = "CAP"
        for icd, disease in KNOWLEDGE_GRAPH["diseases"].items():
            if icd == r["icd_code"]:
                group = disease["group"]
                break
        differentials.append(DifferentialDiagnosis(
            rank=i + 1,
            icd_code=r["icd_code"],
            description=r["description"],
            description_th=r["description_th"],
            probability=r["probability"],
            reasoning=f"พบอาการ {len(r['evidence'])} รายการที่สอดคล้องกับ {r['description']}",
            evidence=r["evidence"],
            cpg_reference=f"Thai CPG {group} 2023",
        ))

    primary_group = "GENERAL"
    if differentials:
        top_icd = differentials[0].icd_code
        for icd, disease in KNOWLEDGE_GRAPH["diseases"].items():
            if icd == top_icd:
                primary_group = disease["group"]
                break

    return PreDiagnosisResponse(
        differentials=differentials,
        primary_disease_group=primary_group,
        confidence_note="คำนวณจาก GraphRAG knowledge graph traversal (MVP)" if differentials else "ไม่พบ differential diagnosis ที่สอดคล้อง",
    )


@router.post("/order-suggestion", response_model=OrderSuggestionResponse)
async def order_suggestion(req: OrderSuggestionRequest) -> OrderSuggestionResponse:
    # Determine disease group
    group = "CAP"
    for icd, disease in KNOWLEDGE_GRAPH["diseases"].items():
        if icd == req.icd_code:
            group = disease["group"]
            break

    template_orders = ORDER_TEMPLATES.get(group, ORDER_TEMPLATES["CAP"])
    personalization: list[str] = []

    orders = []
    for o in template_orders:
        item = OrderItem(
            category=o["category"],
            code=o["code"],
            display_name=o["display_name"],
            priority=o["priority"],
            rationale=o["rationale"],
            cpg_source=o.get("cpg_source"),
        )
        orders.append(item)

    # Personalization
    if req.age >= 65:
        personalization.append("ผู้สูงอายุ ≥65 ปี: ปรับขนาดยาตามไต")
    if req.creatinine and req.creatinine > 1.5:
        personalization.append(f"Cr={req.creatinine}: หลีกเลี่ยงยาทำลายไต, ปรับขนาด")
    if "diabetes" in req.comorbidities:
        personalization.append("DM comorbidity: เพิ่ม DTX monitoring")
    if "ckd" in req.comorbidities:
        personalization.append("CKD comorbidity: ระวังขนาดยาที่ขับทางไต")

    return OrderSuggestionResponse(
        orders=orders,
        disease_group=group,
        personalization_notes=personalization,
    )


@router.post("/admission-decision", response_model=AdmissionDecisionResponse)
async def admission_decision(req: AdmissionDecisionRequest) -> AdmissionDecisionResponse:
    risk_scores: list[RiskScoreDetail] = []

    # Determine disease group
    group = "CAP"
    for icd, disease in KNOWLEDGE_GRAPH["diseases"].items():
        if icd == req.icd_code:
            group = disease["group"]
            break

    if group == "CAP":
        # CURB-65
        c = 1 if req.confusion else 0
        u = 1 if (req.urea and req.urea > 7) else 0
        r = 1 if (req.vitals.respiratory_rate and req.vitals.respiratory_rate >= 30) else 0
        b = 1 if (req.vitals.systolic_bp and req.vitals.systolic_bp < 90) or (req.vitals.diastolic_bp and req.vitals.diastolic_bp <= 60) else 0
        age_score = 1 if req.age >= 65 else 0
        curb65 = c + u + r + b + age_score

        mortality = {0: "<1%", 1: "2.7%", 2: "6.8%", 3: "14%", 4: "27.8%", 5: "27.8%"}
        risk_scores.append(RiskScoreDetail(
            tool_name="CURB-65",
            score=curb65,
            max_score=5,
            components={"Confusion": c, "Urea>7": u, "RR≥30": r, "BP<90/60": b, "Age≥65": age_score},
            interpretation="Low risk" if curb65 <= 1 else "Moderate risk" if curb65 == 2 else "High risk",
            mortality_risk=mortality.get(curb65, "N/A"),
        ))

    # qSOFA (for all)
    q_rr = 1 if (req.vitals.respiratory_rate and req.vitals.respiratory_rate >= 22) else 0
    q_bp = 1 if (req.vitals.systolic_bp and req.vitals.systolic_bp <= 100) else 0
    q_gcs = 1 if (req.vitals.gcs and req.vitals.gcs < 15) else (1 if req.confusion else 0)
    qsofa = q_rr + q_bp + q_gcs

    risk_scores.append(RiskScoreDetail(
        tool_name="qSOFA",
        score=qsofa,
        max_score=3,
        components={"RR≥22": q_rr, "SBP≤100": q_bp, "Altered mentation": q_gcs},
        interpretation="Low risk" if qsofa < 2 else "High risk — evaluate for sepsis",
        mortality_risk="<10%" if qsofa < 2 else ">10%",
    ))

    # Determine recommendation
    max_score = max(rs.score for rs in risk_scores)
    total_max = max(rs.max_score for rs in risk_scores)
    ratio = max_score / total_max if total_max > 0 else 0

    if ratio >= 0.6:
        recommendation = "ICU"
        risk_level = "CRITICAL"
        ward = "ICU / CCU"
        reasoning = "คะแนนความเสี่ยงสูง ควรรับ ICU เพื่อเฝ้าระวังใกล้ชิด"
    elif ratio >= 0.4:
        recommendation = "WARD"
        risk_level = "HIGH"
        ward = "อายุรกรรม (Medicine Ward)"
        reasoning = "คะแนนความเสี่ยงปานกลาง-สูง ควรรับไว้ในหอผู้ป่วย"
    elif ratio >= 0.2:
        recommendation = "OBSERVATION"
        risk_level = "MODERATE"
        ward = "ห้องสังเกตอาการ (Observation)"
        reasoning = "คะแนนความเสี่ยงปานกลาง อาจสังเกตอาการก่อน"
    else:
        recommendation = "OUTPATIENT"
        risk_level = "LOW"
        ward = "OPD Follow-up"
        reasoning = "คะแนนความเสี่ยงต่ำ สามารถรักษาแบบผู้ป่วยนอกได้"

    return AdmissionDecisionResponse(
        recommendation=recommendation,
        risk_level=risk_level,
        risk_scores=risk_scores,
        reasoning=reasoning,
        suggested_ward=ward,
    )
