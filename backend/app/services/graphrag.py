"""GraphRAG service — simplified graph traversal for MVP using in-memory knowledge graph."""

from typing import Optional

# In-memory knowledge graph for MVP (would use Neo4j in production)
KNOWLEDGE_GRAPH: dict[str, dict] = {
    "diseases": {
        "J18.9": {
            "name": "Community-Acquired Pneumonia",
            "name_th": "ปอดอักเสบชุมชน",
            "group": "CAP",
            "symptoms": ["fever", "cough", "dyspnea", "sputum", "chest_pain", "tachypnea"],
            "labs": ["CBC", "CXR", "Blood_culture", "Sputum_culture", "Procalcitonin", "BUN", "Creatinine"],
            "risk_factors": ["age_over_65", "diabetes", "copd", "smoking", "immunosuppressed"],
            "complications": ["sepsis", "respiratory_failure", "pleural_effusion", "empyema"],
        },
        "E11.65": {
            "name": "DM Type 2 with Hyperglycemia",
            "name_th": "เบาหวานชนิดที่ 2 มีน้ำตาลสูง",
            "group": "DM",
            "symptoms": ["polyuria", "polydipsia", "weight_loss", "fatigue", "blurred_vision", "nausea"],
            "labs": ["FBS", "HbA1c", "BUN", "Creatinine", "Electrolytes", "UA", "Ketone"],
            "risk_factors": ["obesity", "family_history_dm", "hypertension", "dyslipidemia"],
            "complications": ["dka", "hhs", "aki", "neuropathy", "retinopathy"],
        },
        "E11.69": {
            "name": "DM Type 2 with Other Complications",
            "name_th": "เบาหวานชนิดที่ 2 มีภาวะแทรกซ้อนอื่น",
            "group": "DM",
            "symptoms": ["polyuria", "polydipsia", "numbness", "foot_ulcer", "fatigue"],
            "labs": ["FBS", "HbA1c", "Lipid_profile", "Creatinine", "Urine_albumin"],
            "risk_factors": ["long_duration_dm", "poor_control", "smoking"],
            "complications": ["nephropathy", "neuropathy", "pvd"],
        },
        "I50.9": {
            "name": "Heart Failure, Unspecified",
            "name_th": "ภาวะหัวใจล้มเหลว",
            "group": "HF",
            "symptoms": ["dyspnea", "orthopnea", "pnd", "edema", "fatigue", "weight_gain", "jvd"],
            "labs": ["BNP", "NT-proBNP", "CXR", "ECG", "Echo", "CBC", "BUN", "Creatinine", "Electrolytes"],
            "risk_factors": ["hypertension", "cad", "diabetes", "valvular_disease", "age_over_65"],
            "complications": ["pulmonary_edema", "cardiogenic_shock", "arrhythmia", "renal_failure"],
        },
        "I50.1": {
            "name": "Left Ventricular Failure",
            "name_th": "หัวใจห้องล่างซ้ายล้มเหลว",
            "group": "HF",
            "symptoms": ["dyspnea", "orthopnea", "pnd", "cough", "fatigue", "tachycardia"],
            "labs": ["BNP", "CXR", "Echo", "ECG"],
            "risk_factors": ["hypertension", "cad", "mi"],
            "complications": ["pulmonary_edema", "cardiogenic_shock"],
        },
        "N17.9": {
            "name": "Acute Kidney Injury",
            "name_th": "ไตวายเฉียบพลัน",
            "group": "DM",
            "symptoms": ["oliguria", "edema", "nausea", "fatigue", "confusion"],
            "labs": ["Creatinine", "BUN", "Electrolytes", "UA", "Urine_output"],
            "risk_factors": ["diabetes", "hypertension", "nephrotoxic_drugs", "dehydration"],
            "complications": ["hyperkalemia", "metabolic_acidosis", "fluid_overload"],
        },
        "E87.2": {
            "name": "Metabolic Acidosis",
            "name_th": "ภาวะกรดจากเมตาบอลิซึม",
            "group": "DM",
            "symptoms": ["kussmaul_breathing", "nausea", "vomiting", "abdominal_pain", "confusion"],
            "labs": ["ABG", "Electrolytes", "Lactate", "Ketone"],
            "risk_factors": ["dka", "renal_failure", "sepsis", "toxic_ingestion"],
            "complications": ["cardiac_arrhythmia", "coma"],
        },
        "A41.9": {
            "name": "Sepsis, Unspecified",
            "name_th": "ภาวะติดเชื้อในกระแสเลือด",
            "group": "CAP",
            "symptoms": ["fever", "tachycardia", "tachypnea", "hypotension", "confusion", "rigors"],
            "labs": ["Blood_culture", "CBC", "Lactate", "Procalcitonin", "CRP"],
            "risk_factors": ["immunosuppressed", "age_over_65", "diabetes", "indwelling_catheter"],
            "complications": ["septic_shock", "mods", "dic"],
        },
    },
    "symptom_weights": {
        "CAP": {"fever": 0.8, "cough": 0.9, "dyspnea": 0.7, "sputum": 0.8, "chest_pain": 0.5, "tachypnea": 0.6},
        "DM": {"polyuria": 0.8, "polydipsia": 0.8, "weight_loss": 0.5, "fatigue": 0.4, "blurred_vision": 0.5, "nausea": 0.4, "numbness": 0.6, "foot_ulcer": 0.7},
        "HF": {"dyspnea": 0.9, "orthopnea": 0.8, "pnd": 0.8, "edema": 0.7, "fatigue": 0.4, "weight_gain": 0.6, "jvd": 0.7},
    },
}


def find_differential_diagnoses(
    symptoms: list[str],
    age: int,
    sex: str,
    pmh: list[str],
    labs: list[dict],
) -> list[dict]:
    """Score diseases against symptoms and return ranked differentials."""
    scores: list[tuple[str, str, str, float, list[str]]] = []

    for icd, disease in KNOWLEDGE_GRAPH["diseases"].items():
        score = 0.0
        matched_evidence: list[str] = []
        symptom_overlap = set(symptoms) & set(disease["symptoms"])

        if not symptom_overlap:
            continue

        # Symptom matching score
        group = disease["group"]
        weights = KNOWLEDGE_GRAPH["symptom_weights"].get(group, {})
        for s in symptom_overlap:
            w = weights.get(s, 0.4)
            score += w
            matched_evidence.append(f"อาการ: {s} (น้ำหนัก {w})")

        # Risk factor bonus
        rf_overlap = set(pmh) & set(disease["risk_factors"])
        for rf in rf_overlap:
            score += 0.3
            matched_evidence.append(f"ปัจจัยเสี่ยง: {rf}")

        if age >= 65 and "age_over_65" in disease["risk_factors"]:
            score += 0.3
            matched_evidence.append("อายุ ≥ 65 ปี")

        # Lab evidence
        lab_codes = {l.get("code", "") for l in labs}
        lab_match = lab_codes & set(disease["labs"])
        if lab_match:
            score += len(lab_match) * 0.2
            for lm in lab_match:
                matched_evidence.append(f"ผลตรวจ: {lm}")

        # Normalize to 0-1
        max_possible = len(disease["symptoms"]) * 0.9 + len(disease["risk_factors"]) * 0.3 + len(disease["labs"]) * 0.2
        probability = min(score / max(max_possible, 1), 0.95)

        scores.append((icd, disease["name"], disease["name_th"], probability, matched_evidence))

    scores.sort(key=lambda x: x[3], reverse=True)
    return [
        {
            "icd_code": s[0],
            "description": s[1],
            "description_th": s[2],
            "probability": round(s[3], 3),
            "evidence": s[4],
        }
        for s in scores[:6]
    ]
