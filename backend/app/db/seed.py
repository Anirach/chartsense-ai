"""Seed database with demo data."""

import json
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.patient import Patient, Encounter, Diagnosis, Observation, OrderRecord, ProgressNote
from app.models.admin import Rule, CPGTemplate
from app.services.rules import CHART_RULES

_seeded = False


def seed_database() -> None:
    global _seeded
    if _seeded:
        return

    db = SessionLocal()
    try:
        if db.query(Patient).count() > 0:
            _seeded = True
            return

        _seed_patients(db)
        _seed_rules(db)
        _seed_templates(db)
        db.commit()
        _seeded = True
        print("✅ Database seeded successfully")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Seed error: {e}")
    finally:
        db.close()


def _seed_patients(db: Session) -> None:
    patients_data = [
        {"hn": "HN-640001", "name": "นายสมชาย ใจดี", "age": 72, "sex": "M", "pmh": ["hypertension", "diabetes", "copd"], "allergies": ["Penicillin"]},
        {"hn": "HN-640002", "name": "นางสมหญิง รักษ์สุข", "age": 65, "sex": "F", "pmh": ["diabetes", "ckd"], "allergies": []},
        {"hn": "HN-640003", "name": "นายประเสริฐ มั่นคง", "age": 78, "sex": "M", "pmh": ["hypertension", "cad", "diabetes"], "allergies": ["Sulfa"]},
        {"hn": "HN-640004", "name": "นางวิภา ศรีสวัสดิ์", "age": 58, "sex": "F", "pmh": ["diabetes", "dyslipidemia"], "allergies": []},
        {"hn": "HN-640005", "name": "นายบุญเลิศ แก้วมณี", "age": 80, "sex": "M", "pmh": ["hypertension", "cad", "hf"], "allergies": ["NSAIDs"]},
        {"hn": "HN-640006", "name": "นางสาวพิมพ์ใจ ทองดี", "age": 45, "sex": "F", "pmh": ["diabetes"], "allergies": []},
        {"hn": "HN-640007", "name": "นายวิชัย สุขสันต์", "age": 68, "sex": "M", "pmh": ["hypertension", "smoking"], "allergies": []},
        {"hn": "HN-640008", "name": "นางนวล จันทร์เพ็ญ", "age": 70, "sex": "F", "pmh": ["hypertension", "diabetes", "valvular_disease"], "allergies": ["Iodine"]},
        {"hn": "HN-640009", "name": "นายธนากร เพชรรัตน์", "age": 55, "sex": "M", "pmh": ["diabetes", "obesity"], "allergies": []},
        {"hn": "HN-640010", "name": "นางสาวอรุณี วงศ์สกุล", "age": 62, "sex": "F", "pmh": ["hypertension", "copd"], "allergies": ["Aspirin"]},
        {"hn": "HN-640011", "name": "นายสุรชัย พงษ์สวัสดิ์", "age": 75, "sex": "M", "pmh": ["diabetes", "cad", "ckd"], "allergies": []},
        {"hn": "HN-640012", "name": "นางรัตนา คำแก้ว", "age": 48, "sex": "F", "pmh": ["diabetes", "hypertension"], "allergies": []},
    ]

    now = datetime.utcnow()

    encounters_data = [
        # CAP cases
        {"patient_idx": 0, "eid": "ENC-2567-0001", "ward": "อายุรกรรมชาย 1", "los": 5, "status": "ACTIVE",
         "cc": "ไข้สูง 3 วัน ไอมีเสมหะเหลืองข้น หอบเหนื่อย",
         "pdx": ("J18.9", "Community-Acquired Pneumonia"), "sdx": [("I10", "Essential Hypertension"), ("E11.9", "DM Type 2")],
         "vitals": [("temperature", "อุณหภูมิ", "38.8", "°C", True), ("heart_rate", "ชีพจร", "105", "bpm", True), ("respiratory_rate", "อัตราหายใจ", "28", "/min", True), ("systolic_bp", "ความดันซิสโตลิค", "145", "mmHg", True), ("diastolic_bp", "ความดันไดแอสโตลิค", "88", "mmHg", False), ("spo2", "SpO2", "92", "%", True)],
         "labs": [("WBC", "WBC", "15800", "/µL", True, "4500-11000"), ("Neutrophil", "Neutrophil", "85", "%", True, "40-70"), ("Hemoglobin", "Hemoglobin", "11.2", "g/dL", False, "12-16"), ("Creatinine", "Creatinine", "1.8", "mg/dL", True, "0.6-1.2"), ("BUN", "BUN", "32", "mg/dL", True, "7-20"), ("FBS", "FBS", "185", "mg/dL", True, "70-100"), ("Potassium", "Potassium", "3.2", "mEq/L", True, "3.5-5.5"), ("Procalcitonin", "Procalcitonin", "4.5", "ng/mL", True, "<0.5"), ("CRP", "CRP", "120", "mg/L", True, "<5")],
         "orders": [("MEDICATION", "Ceftriaxone", "Ceftriaxone 2g IV q24h"), ("MEDICATION", "Azithromycin", "Azithromycin 500mg IV qd"), ("MEDICATION", "Paracetamol", "Paracetamol 500mg q6h PRN"), ("LAB", "Blood_culture", "Blood Culture x2"), ("IMAGING", "CXR", "Chest X-ray PA upright")],
         "notes": [
             ("ผู้ป่วยชายไทย อายุ 72 ปี มาด้วยอาการไข้สูง 3 วัน ไอมีเสมหะเหลืองข้น หอบเหนื่อย\nPE: T 38.8°C, HR 105, RR 28, BP 145/88, SpO2 92% RA\nLung: Crepitation Rt lower lobe\nDx: CAP, HTN, DM\nPlan: ATB, CXR, Blood culture", "นพ.สมศักดิ์ รักษาดี"),
             ("Day 2: ไข้ลดลง T 37.8, ยังไอมีเสมหะ SpO2 94% NC 3L\nCXR: RLL infiltration\nBlood culture: pending\nContinue ATB, monitor", "นพ.สมศักดิ์ รักษาดี"),
         ]},
        {"patient_idx": 1, "eid": "ENC-2567-0002", "ward": "อายุรกรรมหญิง 1", "los": 3, "status": "ACTIVE",
         "cc": "อ่อนเพลีย คลื่นไส้ 2 วัน ปัสสาวะน้อยลง",
         "pdx": ("E11.65", "DM Type 2 with Hyperglycemia"), "sdx": [("N17.9", "Acute Kidney Injury"), ("E87.2", "Metabolic Acidosis")],
         "vitals": [("temperature", "อุณหภูมิ", "37.2", "°C", False), ("heart_rate", "ชีพจร", "92", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "22", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "130", "mmHg", False), ("spo2", "SpO2", "97", "%", False)],
         "labs": [("FBS", "FBS", "320", "mg/dL", True, "70-100"), ("HbA1c", "HbA1c", "11.5", "%", True, "<7"), ("Creatinine", "Creatinine", "2.5", "mg/dL", True, "0.6-1.2"), ("BUN", "BUN", "45", "mg/dL", True, "7-20"), ("Potassium", "Potassium", "5.8", "mEq/L", True, "3.5-5.5"), ("Sodium", "Sodium", "132", "mEq/L", True, "136-145"), ("CO2", "CO2", "15", "mEq/L", True, "22-29"), ("Ketone", "Urine Ketone", "3+", "", True, "Negative")],
         "orders": [("MEDICATION", "Insulin_RI", "Regular Insulin sliding scale"), ("MEDICATION", "NSS", "NSS 1000ml IV 100ml/hr"), ("LAB", "DTX", "DTX q4h"), ("LAB", "ABG", "Arterial Blood Gas")],
         "notes": [
             ("ผู้ป่วยหญิงไทย อายุ 65 ปี DM on Metformin มาด้วยอ่อนเพลีย คลื่นไส้ 2 วัน ปัสสาวะน้อยลง\nDTX 320, Ketone 3+, Cr 2.5\nDx: DM with hyperglycemia, AKI, Metabolic acidosis\nPlan: Insulin, IV fluid, monitor renal function", "พญ.นภา แสงทอง"),
         ]},
        # Heart Failure cases
        {"patient_idx": 2, "eid": "ENC-2567-0003", "ward": "CCU", "los": 7, "status": "ACTIVE",
         "cc": "หอบเหนื่อย นอนราบไม่ได้ 3 วัน ขาบวม 2 ข้าง",
         "pdx": ("I50.1", "Left Ventricular Failure"), "sdx": [("I10", "Essential Hypertension"), ("E11.9", "DM Type 2"), ("I25.1", "ASCVD")],
         "vitals": [("temperature", "อุณหภูมิ", "37.0", "°C", False), ("heart_rate", "ชีพจร", "110", "bpm", True), ("respiratory_rate", "อัตราหายใจ", "30", "/min", True), ("systolic_bp", "ความดันซิสโตลิค", "160", "mmHg", True), ("diastolic_bp", "ความดันไดแอสโตลิค", "95", "mmHg", True), ("spo2", "SpO2", "88", "%", True)],
         "labs": [("BNP", "BNP", "1850", "pg/mL", True, "<100"), ("Troponin", "Troponin-T hs", "0.08", "ng/mL", True, "<0.014"), ("Creatinine", "Creatinine", "1.6", "mg/dL", True, "0.6-1.2"), ("Hemoglobin", "Hemoglobin", "10.5", "g/dL", True, "12-16"), ("Sodium", "Sodium", "133", "mEq/L", True, "136-145"), ("Potassium", "Potassium", "4.8", "mEq/L", False, "3.5-5.5")],
         "orders": [("MEDICATION", "Furosemide", "Furosemide 40mg IV q12h"), ("MEDICATION", "Enalapril", "Enalapril 5mg PO BID"), ("IMAGING", "Echo", "Echocardiogram"), ("IMAGING", "CXR", "Chest X-ray"), ("IMAGING", "ECG", "12-Lead ECG"), ("NURSING", "daily_weight", "ชั่งน้ำหนักทุกเช้า"), ("NURSING", "fluid_restrict", "จำกัดน้ำ 1500ml/วัน")],
         "notes": [
             ("ผู้ป่วยชายไทย อายุ 78 ปี HT, DM, CAD มาด้วยหอบเหนื่อย 3 วัน นอนราบไม่ได้ ขาบวม 2 ข้าง\nPE: JVP elevated, bibasilar crepitation, pitting edema 3+\nBNP 1850, CXR: cardiomegaly with pulmonary congestion\nDx: Acute decompensated HF (ADHF), HFrEF\nPlan: IV diuretics, ACEi, O2 support, Echo", "นพ.ภาณุ หัวใจเข้ม"),
         ]},
        {"patient_idx": 4, "eid": "ENC-2567-0004", "ward": "อายุรกรรมชาย 2", "los": 4, "status": "ACTIVE",
         "cc": "เหนื่อยง่ายขึ้น 1 สัปดาห์ ขาบวม น้ำหนักขึ้น 3 กก.",
         "pdx": ("I50.9", "Heart Failure"), "sdx": [("I10", "Essential Hypertension"), ("I25.1", "ASCVD")],
         "vitals": [("temperature", "อุณหภูมิ", "36.8", "°C", False), ("heart_rate", "ชีพจร", "88", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "22", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "148", "mmHg", True), ("spo2", "SpO2", "94", "%", False)],
         "labs": [("BNP", "BNP", "650", "pg/mL", True, "<100"), ("Creatinine", "Creatinine", "1.3", "mg/dL", True, "0.6-1.2"), ("Hemoglobin", "Hemoglobin", "12.0", "g/dL", False, "12-16")],
         "orders": [("MEDICATION", "Furosemide", "Furosemide 40mg PO BID"), ("MEDICATION", "Carvedilol", "Carvedilol 6.25mg PO BID"), ("DIET", "low_salt", "อาหารจำกัดเกลือ")],
         "notes": [
             ("ผู้ป่วยชาย 80 ปี known HF, CAD มาด้วยเหนื่อยง่ายขึ้น ขาบวม น้ำหนักขึ้น\nBNP 650, mild congestion on CXR\nAdjust diuretic dose, add beta-blocker", "นพ.วรพล อายุรศาสตร์"),
         ]},
        # More CAP
        {"patient_idx": 6, "eid": "ENC-2567-0005", "ward": "อายุรกรรมชาย 1", "los": 3, "status": "ACTIVE",
         "cc": "ไข้ ไอ 5 วัน เจ็บหน้าอกเวลาหายใจลึก",
         "pdx": ("J18.9", "Pneumonia"), "sdx": [("J90", "Pleural Effusion")],
         "vitals": [("temperature", "อุณหภูมิ", "38.2", "°C", True), ("heart_rate", "ชีพจร", "95", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "24", "/min", True), ("systolic_bp", "ความดันซิสโตลิค", "135", "mmHg", False), ("spo2", "SpO2", "93", "%", True)],
         "labs": [("WBC", "WBC", "14200", "/µL", True, "4500-11000"), ("CRP", "CRP", "85", "mg/L", True, "<5"), ("Procalcitonin", "Procalcitonin", "2.1", "ng/mL", True, "<0.5")],
         "orders": [("MEDICATION", "Ceftriaxone", "Ceftriaxone 2g IV q24h"), ("IMAGING", "CXR", "Chest X-ray")],
         "notes": [
             ("ชาย 68 ปี สูบบุหรี่ มาด้วยไข้ ไอ 5 วัน เจ็บหน้าอกขวาเวลาหายใจลึก\nCXR: RLL consolidation with small pleural effusion\nDx: CAP with parapneumonic effusion", "นพ.สมศักดิ์ รักษาดี"),
         ]},
        # DM complications
        {"patient_idx": 3, "eid": "ENC-2567-0006", "ward": "อายุรกรรมหญิง 2", "los": 2, "status": "ACTIVE",
         "cc": "แผลที่เท้าซ้าย 2 สัปดาห์ น้ำตาลคุมไม่ได้",
         "pdx": ("E11.69", "DM with Complications"), "sdx": [("L97.429", "Diabetic Foot Ulcer"), ("E78.5", "Dyslipidemia")],
         "vitals": [("temperature", "อุณหภูมิ", "37.5", "°C", False), ("heart_rate", "ชีพจร", "82", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "18", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "138", "mmHg", False), ("spo2", "SpO2", "98", "%", False)],
         "labs": [("FBS", "FBS", "220", "mg/dL", True, "70-100"), ("HbA1c", "HbA1c", "9.8", "%", True, "<7"), ("Creatinine", "Creatinine", "1.1", "mg/dL", False, "0.6-1.2"), ("WBC", "WBC", "12500", "/µL", True, "4500-11000")],
         "orders": [("MEDICATION", "Insulin_RI", "Insulin sliding scale + basal insulin"), ("NURSING", "wound_care", "Wound care daily"), ("LAB", "HbA1c", "HbA1c")],
         "notes": [
             ("หญิง 58 ปี DM มาด้วยแผลที่เท้าซ้าย 2 สัปดาห์ ไม่หาย น้ำตาลคุมไม่ได้\nHbA1c 9.8, FBS 220\nWound: 3x2 cm ulcer left foot plantar, Grade 2\nDx: DM with foot ulcer, Dyslipidemia\nPlan: Insulin, wound care, consult ortho", "พญ.ปรียา เบาหวานดี"),
         ]},
        # Discharged cases
        {"patient_idx": 7, "eid": "ENC-2567-0007", "ward": "อายุรกรรมหญิง 1", "los": 6, "status": "DISCHARGED",
         "cc": "หอบเหนื่อย นอนราบไม่ได้",
         "pdx": ("I50.9", "Heart Failure"), "sdx": [("I10", "Essential Hypertension"), ("E11.9", "DM Type 2"), ("I34.0", "Mitral Regurgitation")],
         "vitals": [("temperature", "อุณหภูมิ", "36.5", "°C", False), ("heart_rate", "ชีพจร", "78", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "18", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "125", "mmHg", False), ("spo2", "SpO2", "97", "%", False)],
         "labs": [("BNP", "BNP", "280", "pg/mL", True, "<100"), ("Creatinine", "Creatinine", "1.2", "mg/dL", False, "0.6-1.2")],
         "orders": [("MEDICATION", "Furosemide", "Furosemide 20mg PO qd"), ("MEDICATION", "Enalapril", "Enalapril 10mg PO BID")],
         "notes": [
             ("Discharge Summary: หญิง 70 ปี ADHF resolved, EF 35%, MR moderate\nDischarge on: Furosemide 20mg, Enalapril 10mg BID, Carvedilol 12.5mg BID\nF/U OPD 2 wk", "นพ.ภาณุ หัวใจเข้ม"),
         ]},
        {"patient_idx": 8, "eid": "ENC-2567-0008", "ward": "อายุรกรรมชาย 2", "los": 4, "status": "ACTIVE",
         "cc": "ซึม สับสน น้ำตาลสูงมาก",
         "pdx": ("E11.65", "DM with Hyperglycemia"), "sdx": [("E87.2", "Metabolic Acidosis")],
         "vitals": [("temperature", "อุณหภูมิ", "37.8", "°C", False), ("heart_rate", "ชีพจร", "110", "bpm", True), ("respiratory_rate", "อัตราหายใจ", "26", "/min", True), ("systolic_bp", "ความดันซิสโตลิค", "100", "mmHg", True), ("spo2", "SpO2", "96", "%", False)],
         "labs": [("FBS", "FBS", "480", "mg/dL", True, "70-100"), ("HbA1c", "HbA1c", "13.2", "%", True, "<7"), ("Creatinine", "Creatinine", "2.1", "mg/dL", True, "0.6-1.2"), ("Potassium", "Potassium", "5.2", "mEq/L", False, "3.5-5.5"), ("CO2", "CO2", "12", "mEq/L", True, "22-29"), ("Ketone", "Urine Ketone", "4+", "", True, "Negative")],
         "orders": [("MEDICATION", "Insulin_drip", "Insulin drip 0.1 U/kg/hr"), ("MEDICATION", "NSS", "NSS 1000ml IV bolus then 200ml/hr"), ("LAB", "DTX", "DTX q1h"), ("LAB", "ABG", "ABG q6h")],
         "notes": [
             ("ชาย 55 ปี DM มาด้วยซึม สับสน DTX 480\nKetone 4+, CO2 12, pH 7.18\nDx: DKA\nPlan: Insulin drip, aggressive hydration, K+ monitoring", "พญ.นภา แสงทอง"),
         ]},
        {"patient_idx": 9, "eid": "ENC-2567-0009", "ward": "อายุรกรรมหญิง 2", "los": 4, "status": "ACTIVE",
         "cc": "ไข้สูง ไอ หอบ 2 วัน",
         "pdx": ("J18.9", "Pneumonia"), "sdx": [("A41.9", "Sepsis"), ("I10", "Essential Hypertension")],
         "vitals": [("temperature", "อุณหภูมิ", "39.5", "°C", True), ("heart_rate", "ชีพจร", "115", "bpm", True), ("respiratory_rate", "อัตราหายใจ", "32", "/min", True), ("systolic_bp", "ความดันซิสโตลิค", "95", "mmHg", True), ("spo2", "SpO2", "89", "%", True)],
         "labs": [("WBC", "WBC", "18500", "/µL", True, "4500-11000"), ("Procalcitonin", "Procalcitonin", "8.5", "ng/mL", True, "<0.5"), ("Lactate", "Lactate", "3.2", "mmol/L", True, "<2"), ("Creatinine", "Creatinine", "1.9", "mg/dL", True, "0.6-1.2")],
         "orders": [("MEDICATION", "Meropenem", "Meropenem 1g IV q8h"), ("MEDICATION", "NSS", "NSS 30ml/kg bolus"), ("LAB", "Blood_culture", "Blood Culture x2")],
         "notes": [
             ("หญิง 62 ปี COPD มาด้วยไข้สูง ไอ หอบรุนแรง 2 วัน\nqSOFA 3 (RR 32, SBP 95, altered mentation)\nLactate 3.2, Procalcitonin 8.5\nDx: Severe CAP with sepsis\nPlan: Broad-spectrum ATB, fluid resuscitation, ICU transfer", "นพ.สมศักดิ์ รักษาดี"),
         ]},
        {"patient_idx": 10, "eid": "ENC-2567-0010", "ward": "อายุรกรรมชาย 1", "los": 5, "status": "ACTIVE",
         "cc": "เท้าชา แผลเรื้อรัง ไตเสื่อม",
         "pdx": ("E11.22", "DM with CKD"), "sdx": [("N18.3", "CKD Stage 3"), ("E11.42", "DM Neuropathy")],
         "vitals": [("temperature", "อุณหภูมิ", "36.8", "°C", False), ("heart_rate", "ชีพจร", "78", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "18", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "155", "mmHg", True), ("spo2", "SpO2", "97", "%", False)],
         "labs": [("FBS", "FBS", "165", "mg/dL", True, "70-100"), ("HbA1c", "HbA1c", "8.5", "%", True, "<7"), ("Creatinine", "Creatinine", "2.8", "mg/dL", True, "0.6-1.2"), ("BUN", "BUN", "38", "mg/dL", True, "7-20"), ("Potassium", "Potassium", "5.1", "mEq/L", False, "3.5-5.5"), ("Urine_albumin", "UACR", "350", "mg/g", True, "<30")],
         "orders": [("MEDICATION", "Insulin", "Insulin Glargine 20U HS"), ("MEDICATION", "Losartan", "Losartan 50mg PO qd"), ("LAB", "GFR", "eGFR calculation")],
         "notes": [
             ("ชาย 75 ปี DM 20 ปี มาด้วย neuropathy, CKD stage 3\nCr 2.8, UACR 350, eGFR 28\nDx: DM with CKD stage 3, DM neuropathy\nPlan: adjust medication for renal function, ARB for nephroprotection", "พญ.ปรียา เบาหวานดี"),
         ]},
        {"patient_idx": 11, "eid": "ENC-2567-0011", "ward": "อายุรกรรมหญิง 1", "los": 2, "status": "ACTIVE",
         "cc": "น้ำตาลสูง อ่อนเพลีย ตามัว",
         "pdx": ("E11.65", "DM with Hyperglycemia"), "sdx": [("I10", "Essential Hypertension")],
         "vitals": [("temperature", "อุณหภูมิ", "36.9", "°C", False), ("heart_rate", "ชีพจร", "85", "bpm", False), ("respiratory_rate", "อัตราหายใจ", "18", "/min", False), ("systolic_bp", "ความดันซิสโตลิค", "142", "mmHg", True), ("spo2", "SpO2", "98", "%", False)],
         "labs": [("FBS", "FBS", "280", "mg/dL", True, "70-100"), ("HbA1c", "HbA1c", "10.2", "%", True, "<7"), ("Creatinine", "Creatinine", "0.9", "mg/dL", False, "0.6-1.2")],
         "orders": [("MEDICATION", "Insulin_RI", "Insulin sliding scale"), ("LAB", "DTX", "DTX q6h"), ("LAB", "Lipid", "Lipid Profile")],
         "notes": [
             ("หญิง 48 ปี DM, HT มาด้วยน้ำตาลสูง อ่อนเพลีย ตามัว\nFBS 280, HbA1c 10.2\nDx: DM with hyperglycemia, uncontrolled\nPlan: Insulin, consult ophthalmology", "พญ.ปรียา เบาหวานดี"),
         ]},
    ]

    for pd in patients_data:
        p = Patient(**pd)
        db.add(p)
    db.flush()

    patients = db.query(Patient).all()

    for ed in encounters_data:
        p = patients[ed["patient_idx"]]
        admit = now - timedelta(days=ed["los"])
        enc = Encounter(
            encounter_id=ed["eid"],
            patient_id=p.id,
            admit_date=admit,
            dc_date=(now - timedelta(days=1)) if ed["status"] == "DISCHARGED" else None,
            ward=ed["ward"],
            los=ed["los"],
            status=ed["status"],
            chief_complaint=ed["cc"],
        )
        db.add(enc)
        db.flush()

        # PDx
        pdx_code, pdx_desc = ed["pdx"]
        db.add(Diagnosis(encounter_id=enc.id, icd_code=pdx_code, description=pdx_desc, dx_type="PDx", source="MD"))
        for sdx_code, sdx_desc in ed.get("sdx", []):
            db.add(Diagnosis(encounter_id=enc.id, icd_code=sdx_code, description=sdx_desc, dx_type="SDx", source="MD"))

        # Vitals
        for code, display, val, unit, abnormal in ed.get("vitals", []):
            db.add(Observation(encounter_id=enc.id, obs_type="vital", code=code, display_name=display, value=val, unit=unit, date_time=admit, abnormal_flag=abnormal))

        # Labs
        for item in ed.get("labs", []):
            code, display, val, unit, abnormal = item[0], item[1], item[2], item[3], item[4]
            ref_range = item[5] if len(item) > 5 else None
            db.add(Observation(encounter_id=enc.id, obs_type="lab", code=code, display_name=display, value=val, unit=unit, date_time=admit, abnormal_flag=abnormal, reference_range=ref_range))

        # Orders
        for cat, code, display in ed.get("orders", []):
            db.add(OrderRecord(encounter_id=enc.id, category=cat, standard_code=code, display_name=display, status="ORDERED"))

        # Notes
        for i, (text, author) in enumerate(ed.get("notes", [])):
            db.add(ProgressNote(encounter_id=enc.id, date_time=admit + timedelta(days=i), text=text, author=author))


def _seed_rules(db: Session) -> None:
    for r in CHART_RULES:
        db.add(Rule(
            rule_id=r["ruleId"],
            category=r["category"],
            name=r["name"],
            weight=r["weight"],
            condition=r["condition"],
            active=True,
        ))


def _seed_templates(db: Session) -> None:
    templates = [
        {"template_id": "CPG-CAP-2023", "disease_group": "CAP", "name": "Thai CPG: Community-Acquired Pneumonia 2023",
         "description": "แนวทางการรักษาปอดอักเสบชุมชนในผู้ใหญ่ สมาคมอุรเวชช์แห่งประเทศไทย 2566",
         "orders": [
             {"category": "LAB", "code": "CBC", "name": "CBC", "priority": "ESSENTIAL"},
             {"category": "LAB", "code": "Blood_culture", "name": "Blood Culture x2", "priority": "ESSENTIAL"},
             {"category": "IMAGING", "code": "CXR", "name": "Chest X-ray", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "Ceftriaxone", "name": "Ceftriaxone 2g IV q24h", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "Azithromycin", "name": "Azithromycin 500mg", "priority": "ESSENTIAL"},
         ],
         "criteria": {"severity": "CURB-65", "admission_threshold": 2}},
        {"template_id": "CPG-DM-2023", "disease_group": "DM", "name": "Thai CPG: DM Complications Management 2023",
         "description": "แนวทางการดูแลผู้ป่วยเบาหวานและภาวะแทรกซ้อน สมาคมโรคเบาหวานแห่งประเทศไทย 2566",
         "orders": [
             {"category": "LAB", "code": "FBS", "name": "Fasting Blood Sugar", "priority": "ESSENTIAL"},
             {"category": "LAB", "code": "HbA1c", "name": "HbA1c", "priority": "ESSENTIAL"},
             {"category": "LAB", "code": "Cr", "name": "Creatinine", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "Insulin", "name": "Insulin as indicated", "priority": "ESSENTIAL"},
         ],
         "criteria": {"target_hba1c": 7.0, "renal_monitoring": True}},
        {"template_id": "CPG-HF-2023", "disease_group": "HF", "name": "Thai CPG: Heart Failure Management 2023",
         "description": "แนวทางการรักษาภาวะหัวใจล้มเหลว สมาคมแพทย์โรคหัวใจแห่งประเทศไทย 2566",
         "orders": [
             {"category": "LAB", "code": "BNP", "name": "BNP/NT-proBNP", "priority": "ESSENTIAL"},
             {"category": "IMAGING", "code": "Echo", "name": "Echocardiogram", "priority": "ESSENTIAL"},
             {"category": "IMAGING", "code": "ECG", "name": "12-Lead ECG", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "Furosemide", "name": "Furosemide IV/PO", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "ACEi", "name": "ACEi/ARB", "priority": "ESSENTIAL"},
             {"category": "MEDICATION", "code": "Beta-blocker", "name": "Carvedilol/Bisoprolol", "priority": "RECOMMENDED"},
         ],
         "criteria": {"ef_threshold": 40, "bnp_threshold": 400}},
    ]

    for t in templates:
        db.add(CPGTemplate(
            template_id=t["template_id"],
            disease_group=t["disease_group"],
            name=t["name"],
            description=t.get("description", ""),
            orders=t["orders"],
            criteria=t["criteria"],
        ))
