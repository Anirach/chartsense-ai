"""DRG/RW calculator for code suggestion impact analysis."""

from typing import Any

# Simplified RW lookup for demo
RW_TABLE: dict[str, dict[str, float]] = {
    "J18.9": {"rw": 0.8956, "name": "Pneumonia"},
    "J18.0": {"rw": 0.9234, "name": "Bronchopneumonia"},
    "A41.9": {"rw": 2.1543, "name": "Sepsis"},
    "R65.20": {"rw": 3.2100, "name": "Severe sepsis"},
    "I50.9": {"rw": 1.0245, "name": "Heart failure"},
    "I50.1": {"rw": 1.1500, "name": "Left ventricular failure"},
    "I50.21": {"rw": 1.3200, "name": "Acute systolic HF"},
    "E11.65": {"rw": 0.7823, "name": "DM with hyperglycemia"},
    "E11.69": {"rw": 0.8100, "name": "DM with complications"},
    "E11.22": {"rw": 1.4500, "name": "DM with CKD"},
    "N17.9": {"rw": 1.2345, "name": "AKI"},
    "N18.3": {"rw": 0.9500, "name": "CKD stage 3"},
    "E87.2": {"rw": 0.6700, "name": "Metabolic acidosis"},
    "E87.6": {"rw": 0.5500, "name": "Hypokalemia"},
    "E87.5": {"rw": 0.6800, "name": "Hyperkalemia"},
    "I10": {"rw": 0.4500, "name": "Hypertension"},
    "E78.5": {"rw": 0.3200, "name": "Dyslipidemia"},
    "D64.9": {"rw": 0.5000, "name": "Anemia"},
    "J96.0": {"rw": 2.5600, "name": "Acute respiratory failure"},
    "J90": {"rw": 0.7800, "name": "Pleural effusion"},
}

# Base rate per RW unit in THB
BASE_RATE_THB = 12_000.0


def calculate_rw(
    current_codes: list[str],
    suggested_codes: list[str],
) -> dict[str, Any]:
    """Calculate RW before/after adding suggested codes."""
    rw_before = sum(RW_TABLE.get(c, {}).get("rw", 0) for c in current_codes)
    all_codes = list(set(current_codes + suggested_codes))
    rw_after = sum(RW_TABLE.get(c, {}).get("rw", 0) for c in all_codes)
    delta = rw_after - rw_before
    revenue = delta * BASE_RATE_THB

    return {
        "rw_before": round(rw_before, 4),
        "rw_after": round(rw_after, 4),
        "delta": round(delta, 4),
        "revenue_impact_thb": round(revenue, 2),
    }


def get_code_suggestions(
    encounter_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate code suggestions based on encounter data."""
    suggestions: list[dict[str, Any]] = []
    current_codes = [d.get("icd_code", "") for d in encounter_data.get("diagnoses", [])]

    observations = encounter_data.get("observations", [])
    lab_values: dict[str, float] = {}
    for obs in observations:
        if obs.get("obs_type") == "lab":
            try:
                lab_values[obs["code"]] = float(obs.get("value", 0))
            except (ValueError, TypeError):
                pass

    # Check for missing codes based on lab values
    code_rules: list[dict[str, Any]] = [
        {"lab": "Creatinine", "op": ">=", "val": 1.5, "code": "N17.9", "desc": "Acute Kidney Injury", "conf_base": 0.75},
        {"lab": "FBS", "op": ">=", "val": 126, "code": "E11.9", "desc": "DM Type 2", "conf_base": 0.70},
        {"lab": "HbA1c", "op": ">=", "val": 6.5, "code": "E11.65", "desc": "DM with Hyperglycemia", "conf_base": 0.80},
        {"lab": "Potassium", "op": "<", "val": 3.5, "code": "E87.6", "desc": "Hypokalemia", "conf_base": 0.85},
        {"lab": "Potassium", "op": ">", "val": 5.5, "code": "E87.5", "desc": "Hyperkalemia", "conf_base": 0.85},
        {"lab": "Hemoglobin", "op": "<", "val": 10, "code": "D64.9", "desc": "Anemia, Unspecified", "conf_base": 0.70},
        {"lab": "BNP", "op": ">", "val": 400, "code": "I50.9", "desc": "Heart Failure", "conf_base": 0.80},
        {"lab": "Procalcitonin", "op": ">", "val": 2.0, "code": "A41.9", "desc": "Sepsis", "conf_base": 0.75},
    ]

    for rule in code_rules:
        lab_code = rule["lab"]
        if lab_code not in lab_values:
            continue
        val = lab_values[lab_code]
        op = rule["op"]
        threshold = rule["val"]
        triggered = False
        if op == ">=" and val >= threshold:
            triggered = True
        elif op == ">" and val > threshold:
            triggered = True
        elif op == "<" and val < threshold:
            triggered = True

        if triggered and rule["code"] not in current_codes:
            # Calculate confidence
            conf = rule["conf_base"]
            # Documentation bonus
            has_notes = len(encounter_data.get("progress_notes", [])) > 0
            if has_notes:
                conf += 0.05
            # Treatment bonus: check if related meds ordered
            has_orders = len(encounter_data.get("orders", [])) > 0
            if has_orders:
                conf += 0.05

            rw = RW_TABLE.get(rule["code"], {}).get("rw", 0)
            evidence = [
                f"{lab_code} = {val} ({op} {threshold})",
                "พบจากผลตรวจทางห้องปฏิบัติการ",
            ]
            if has_notes:
                evidence.append("มี Progress Note สนับสนุน")
            if has_orders:
                evidence.append("มีการสั่งยา/การรักษาที่สอดคล้อง")

            suggestions.append({
                "icd_code": rule["code"],
                "description": rule["desc"],
                "dx_type": "SDx",
                "confidence": round(min(conf, 0.95), 3),
                "evidence": evidence,
                "rw_impact": round(rw, 4),
                "status": "PENDING",
            })

    return suggestions
