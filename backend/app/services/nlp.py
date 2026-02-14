"""Thai NLP service — keyword-based for MVP."""

SYMPTOM_KEYWORDS_TH: dict[str, list[str]] = {
    "fever": ["ไข้", "ตัวร้อน", "มีไข้", "febrile"],
    "cough": ["ไอ", "ไอมีเสมหะ", "ไอแห้ง"],
    "dyspnea": ["หอบ", "เหนื่อย", "หายใจลำบาก", "หายใจเร็ว", "SOB"],
    "sputum": ["เสมหะ", "มีเสมหะ", "เสมหะเหลือง"],
    "chest_pain": ["เจ็บหน้าอก", "แน่นหน้าอก"],
    "edema": ["บวม", "ขาบวม", "บวมกดบุ๋ม", "pitting edema"],
    "orthopnea": ["นอนราบไม่ได้", "หายใจไม่ออกเวลานอน"],
    "pnd": ["PND", "สะดุ้งตื่นกลางคืน"],
    "polyuria": ["ปัสสาวะบ่อย", "ปัสสาวะมาก"],
    "polydipsia": ["กระหายน้ำ", "ดื่มน้ำมาก"],
    "weight_loss": ["น้ำหนักลด", "ผอมลง"],
    "fatigue": ["อ่อนเพลีย", "เหนื่อยง่าย", "ไม่มีแรง"],
    "confusion": ["สับสน", "ซึม", "altered consciousness"],
    "nausea": ["คลื่นไส้", "อาเจียน"],
    "hypotension": ["ความดันต่ำ", "BP drop"],
}


def extract_symptoms_from_text(text: str) -> list[str]:
    """Extract symptom codes from Thai clinical text."""
    found: list[str] = []
    text_lower = text.lower()
    for symptom_code, keywords in SYMPTOM_KEYWORDS_TH.items():
        for kw in keywords:
            if kw.lower() in text_lower or kw in text:
                found.append(symptom_code)
                break
    return found


def extract_entities(text: str) -> list[dict[str, str]]:
    """Extract NLP entities from Thai text (simplified)."""
    entities: list[dict[str, str]] = []
    symptoms = extract_symptoms_from_text(text)
    for s in symptoms:
        entities.append({"type": "SYMPTOM", "value": s, "source": "NLP"})
    return entities
