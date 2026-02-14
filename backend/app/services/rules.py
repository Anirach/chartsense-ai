"""Chart completeness rule engine."""

from typing import Any

# In-memory rules for MVP
CHART_RULES: list[dict[str, Any]] = [
    {"ruleId": "DX-01", "category": "DIAGNOSIS", "name": "PDx ต้องมีอย่างน้อย 1 รายการ", "weight": 15, "condition": {"type": "REQUIRED_FIELD", "field": "primary_dx", "requiredAction": "ADD_PDX"}},
    {"ruleId": "DX-02", "category": "DIAGNOSIS", "name": "SDx: Hypertension (if BP↑)", "weight": 8, "condition": {"type": "VITAL_THRESHOLD", "vitalCode": "systolic_bp", "operator": ">=", "threshold": 140, "requiredAction": "ADD_SDX", "suggestedCode": "I10"}},
    {"ruleId": "DX-03", "category": "DIAGNOSIS", "name": "SDx: DM (if FBS↑)", "weight": 8, "condition": {"type": "LAB_THRESHOLD", "labCode": "FBS", "operator": ">=", "threshold": 126, "requiredAction": "ADD_SDX", "suggestedCode": "E11.9"}},
    {"ruleId": "DX-04", "category": "DIAGNOSIS", "name": "SDx: AKI (if Cr↑)", "weight": 10, "condition": {"type": "LAB_THRESHOLD", "labCode": "Creatinine", "operator": "INCREASE_FROM_BASELINE", "threshold": 0.3, "requiredAction": "ADD_SDX", "suggestedCode": "N17.9"}},
    {"ruleId": "DX-05", "category": "DIAGNOSIS", "name": "SDx: Anemia (if Hb↓)", "weight": 6, "condition": {"type": "LAB_THRESHOLD", "labCode": "Hemoglobin", "operator": "<", "threshold": 10, "requiredAction": "ADD_SDX", "suggestedCode": "D64.9"}},
    {"ruleId": "DX-06", "category": "DIAGNOSIS", "name": "SDx: Hypokalemia (if K↓)", "weight": 7, "condition": {"type": "LAB_THRESHOLD", "labCode": "Potassium", "operator": "<", "threshold": 3.5, "requiredAction": "ADD_SDX", "suggestedCode": "E87.6"}},
    {"ruleId": "DX-07", "category": "DIAGNOSIS", "name": "SDx: Hyperkalemia (if K↑)", "weight": 7, "condition": {"type": "LAB_THRESHOLD", "labCode": "Potassium", "operator": ">", "threshold": 5.5, "requiredAction": "ADD_SDX", "suggestedCode": "E87.5"}},
    {"ruleId": "DX-08", "category": "DIAGNOSIS", "name": "SDx: Sepsis (if qSOFA≥2)", "weight": 12, "condition": {"type": "SCORE_THRESHOLD", "scoreCode": "qSOFA", "operator": ">=", "threshold": 2, "requiredAction": "ADD_SDX", "suggestedCode": "A41.9"}},
    {"ruleId": "PR-01", "category": "PROCEDURE", "name": "ต้องลง Procedure ถ้ามีหัตถการ", "weight": 10, "condition": {"type": "REQUIRED_IF", "trigger": "has_procedure_order", "requiredAction": "ADD_PROCEDURE"}},
    {"ruleId": "PR-02", "category": "PROCEDURE", "name": "Ventilator procedure code", "weight": 10, "condition": {"type": "REQUIRED_IF", "trigger": "ventilator_order", "requiredAction": "ADD_PROCEDURE", "suggestedCode": "5A1955Z"}},
    {"ruleId": "CO-01", "category": "CONSISTENCY", "name": "Dx สอดคล้องกับ Lab", "weight": 10, "condition": {"type": "CONSISTENCY_CHECK", "check": "dx_lab_match"}},
    {"ruleId": "CO-02", "category": "CONSISTENCY", "name": "Dx สอดคล้องกับ Medication", "weight": 8, "condition": {"type": "CONSISTENCY_CHECK", "check": "dx_med_match"}},
    {"ruleId": "CO-03", "category": "CONSISTENCY", "name": "PDx ตรง Chief Complaint", "weight": 7, "condition": {"type": "CONSISTENCY_CHECK", "check": "pdx_cc_match"}},
    {"ruleId": "CO-04", "category": "CONSISTENCY", "name": "LOS สอดคล้องกับ Severity", "weight": 5, "condition": {"type": "CONSISTENCY_CHECK", "check": "los_severity_match"}},
    {"ruleId": "CO-05", "category": "CONSISTENCY", "name": "ลำดับ Dx ถูกต้อง", "weight": 5, "condition": {"type": "CONSISTENCY_CHECK", "check": "dx_order_correct"}},
    {"ruleId": "DO-01", "category": "DOCUMENTATION", "name": "Progress Note มีครบทุกวัน", "weight": 8, "condition": {"type": "REQUIRED_FIELD", "field": "daily_notes"}},
    {"ruleId": "DO-02", "category": "DOCUMENTATION", "name": "Discharge Summary มี", "weight": 8, "condition": {"type": "REQUIRED_IF", "trigger": "discharged", "requiredAction": "ADD_DISCHARGE_SUMMARY"}},
    {"ruleId": "DO-03", "category": "DOCUMENTATION", "name": "Vital Signs บันทึกครบ", "weight": 5, "condition": {"type": "REQUIRED_FIELD", "field": "vitals_complete"}},
    {"ruleId": "DO-04", "category": "DOCUMENTATION", "name": "Allergy ระบุในแฟ้ม", "weight": 4, "condition": {"type": "REQUIRED_FIELD", "field": "allergy_documented"}},
    {"ruleId": "DO-05", "category": "DOCUMENTATION", "name": "Informed Consent บันทึก", "weight": 5, "condition": {"type": "REQUIRED_IF", "trigger": "has_procedure", "requiredAction": "ADD_CONSENT"}},
]


def evaluate_chart(encounter_data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate chart completeness based on rules. Returns score and gaps."""
    gaps: list[dict[str, Any]] = []
    category_scores: dict[str, dict[str, float]] = {
        "DIAGNOSIS": {"earned": 0, "possible": 0, "weight": 0.30},
        "PROCEDURE": {"earned": 0, "possible": 0, "weight": 0.20},
        "CONSISTENCY": {"earned": 0, "possible": 0, "weight": 0.25},
        "DOCUMENTATION": {"earned": 0, "possible": 0, "weight": 0.25},
    }

    diagnoses = encounter_data.get("diagnoses", [])
    observations = encounter_data.get("observations", [])
    orders = encounter_data.get("orders", [])
    notes = encounter_data.get("progress_notes", [])
    status = encounter_data.get("status", "ACTIVE")

    # Build lookup dicts
    lab_values: dict[str, float] = {}
    vital_values: dict[str, float] = {}
    for obs in observations:
        try:
            val = float(obs.get("value", 0))
        except (ValueError, TypeError):
            continue
        if obs.get("obs_type") == "lab":
            lab_values[obs["code"]] = val
        elif obs.get("obs_type") == "vital":
            vital_values[obs["code"]] = val

    dx_codes = {d.get("icd_code", "") for d in diagnoses}
    has_pdx = any(d.get("dx_type") == "PDx" for d in diagnoses)

    for rule in CHART_RULES:
        cat = rule["category"]
        weight = rule["weight"]
        category_scores[cat]["possible"] += weight
        passed = True

        cond = rule["condition"]
        cond_type = cond.get("type", "")

        if cond_type == "REQUIRED_FIELD":
            field = cond.get("field", "")
            if field == "primary_dx":
                passed = has_pdx
            elif field == "daily_notes":
                passed = len(notes) > 0
            elif field == "vitals_complete":
                passed = len(vital_values) >= 3
            elif field == "allergy_documented":
                passed = True  # assume documented for MVP
            else:
                passed = True

        elif cond_type == "LAB_THRESHOLD":
            lab_code = cond.get("labCode", "")
            if lab_code in lab_values:
                op = cond.get("operator", ">=")
                threshold = cond.get("threshold", 0)
                val = lab_values[lab_code]
                if op == ">=" and val >= threshold:
                    suggested = cond.get("suggestedCode", "")
                    passed = suggested in dx_codes
                elif op == "<" and val < threshold:
                    suggested = cond.get("suggestedCode", "")
                    passed = suggested in dx_codes
                elif op == ">" and val > threshold:
                    suggested = cond.get("suggestedCode", "")
                    passed = suggested in dx_codes
                elif op == "INCREASE_FROM_BASELINE":
                    passed = cond.get("suggestedCode", "") in dx_codes
                else:
                    passed = True
            else:
                passed = True  # lab not available, rule N/A

        elif cond_type == "VITAL_THRESHOLD":
            vital_code = cond.get("vitalCode", "")
            if vital_code in vital_values:
                op = cond.get("operator", ">=")
                threshold = cond.get("threshold", 0)
                val = vital_values[vital_code]
                if op == ">=" and val >= threshold:
                    suggested = cond.get("suggestedCode", "")
                    passed = suggested in dx_codes
                else:
                    passed = True
            else:
                passed = True

        elif cond_type == "REQUIRED_IF":
            trigger = cond.get("trigger", "")
            if trigger == "discharged" and status == "DISCHARGED":
                passed = len(notes) > 0  # simplified
            elif trigger == "has_procedure_order":
                passed = True  # simplified for MVP
            else:
                passed = True

        elif cond_type == "CONSISTENCY_CHECK":
            # Simplified: assume most consistency checks pass
            check = cond.get("check", "")
            if check == "dx_lab_match":
                passed = len(diagnoses) > 0 and len(observations) > 0
            elif check == "dx_med_match":
                passed = len(diagnoses) > 0 and len(orders) > 0
            else:
                passed = True

        elif cond_type == "SCORE_THRESHOLD":
            passed = True  # simplified

        if passed:
            category_scores[cat]["earned"] += weight
        else:
            gaps.append({
                "rule_id": rule["ruleId"],
                "category": cat,
                "description": rule["name"],
                "severity": "CRITICAL" if weight >= 10 else "WARNING",
                "suggested_action": cond.get("requiredAction"),
                "suggested_code": cond.get("suggestedCode"),
            })

    # Calculate weighted total
    total = 0.0
    breakdown_list: list[dict[str, Any]] = []
    for cat, data in category_scores.items():
        if data["possible"] > 0:
            cat_pct = (data["earned"] / data["possible"]) * 100
        else:
            cat_pct = 100.0
        weighted = cat_pct * data["weight"]
        total += weighted
        breakdown_list.append({
            "category": cat,
            "score": round(cat_pct, 1),
            "max_score": 100.0,
            "weight": data["weight"],
            "items_found": int(data["earned"]),
            "items_expected": int(data["possible"]),
        })

    grade = "A" if total >= 90 else "B" if total >= 75 else "C" if total >= 60 else "D" if total >= 40 else "F"

    return {
        "total_score": round(total, 1),
        "grade": grade,
        "breakdown": breakdown_list,
        "gaps": gaps,
    }
