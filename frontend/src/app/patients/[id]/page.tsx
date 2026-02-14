"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn, getScoreColor, getSeverityColor, getPriorityColor, formatCurrency, getStatusColor } from "@/lib/utils";
import type {
  PreDiagnosisResponse, OrderSuggestionResponse, AdmissionDecisionResponse,
  ChartScoreResponse, CodeSuggestionResponse, DifferentialDiagnosis,
} from "@/types";

// Demo patient data
const DEMO_ENCOUNTERS: Record<string, {
  patient: { hn: string; name: string; age: number; sex: string; pmh: string[]; allergies: string[] };
  encounter_id: string; ward: string; los: number; status: string; cc: string; pdx: string; pdx_icd: string;
}> = {
  "ENC-2567-0001": { patient: { hn: "HN-640001", name: "นายสมชาย ใจดี", age: 72, sex: "M", pmh: ["hypertension", "diabetes", "copd"], allergies: ["Penicillin"] }, encounter_id: "ENC-2567-0001", ward: "อายุรกรรมชาย 1", los: 5, status: "ACTIVE", cc: "ไข้สูง 3 วัน ไอมีเสมหะเหลืองข้น หอบเหนื่อย", pdx: "Community-Acquired Pneumonia", pdx_icd: "J18.9" },
  "ENC-2567-0002": { patient: { hn: "HN-640002", name: "นางสมหญิง รักษ์สุข", age: 65, sex: "F", pmh: ["diabetes", "ckd"], allergies: [] }, encounter_id: "ENC-2567-0002", ward: "อายุรกรรมหญิง 1", los: 3, status: "ACTIVE", cc: "อ่อนเพลีย คลื่นไส้ 2 วัน ปัสสาวะน้อยลง", pdx: "DM Type 2 with Hyperglycemia", pdx_icd: "E11.65" },
  "ENC-2567-0003": { patient: { hn: "HN-640003", name: "นายประเสริฐ มั่นคง", age: 78, sex: "M", pmh: ["hypertension", "cad", "diabetes"], allergies: ["Sulfa"] }, encounter_id: "ENC-2567-0003", ward: "CCU", los: 7, status: "ACTIVE", cc: "หอบเหนื่อย นอนราบไม่ได้ 3 วัน ขาบวม 2 ข้าง", pdx: "Left Ventricular Failure", pdx_icd: "I50.1" },
  "ENC-2567-0004": { patient: { hn: "HN-640005", name: "นายบุญเลิศ แก้วมณี", age: 80, sex: "M", pmh: ["hypertension", "cad", "hf"], allergies: ["NSAIDs"] }, encounter_id: "ENC-2567-0004", ward: "อายุรกรรมชาย 2", los: 4, status: "ACTIVE", cc: "เหนื่อยง่ายขึ้น 1 สัปดาห์ ขาบวม น้ำหนักขึ้น 3 กก.", pdx: "Heart Failure", pdx_icd: "I50.9" },
  "ENC-2567-0005": { patient: { hn: "HN-640007", name: "นายวิชัย สุขสันต์", age: 68, sex: "M", pmh: ["hypertension", "smoking"], allergies: [] }, encounter_id: "ENC-2567-0005", ward: "อายุรกรรมชาย 1", los: 3, status: "ACTIVE", cc: "ไข้ ไอ 5 วัน เจ็บหน้าอกเวลาหายใจลึก", pdx: "Pneumonia", pdx_icd: "J18.9" },
  "ENC-2567-0009": { patient: { hn: "HN-640010", name: "นางสาวอรุณี วงศ์สกุล", age: 62, sex: "F", pmh: ["hypertension", "copd"], allergies: ["Aspirin"] }, encounter_id: "ENC-2567-0009", ward: "อายุรกรรมหญิง 2", los: 4, status: "ACTIVE", cc: "ไข้สูง ไอ หอบ 2 วัน", pdx: "Pneumonia with Sepsis", pdx_icd: "J18.9" },
};

// Demo API responses
const DEMO_PREDIAG: Record<string, PreDiagnosisResponse> = {
  "ENC-2567-0001": {
    differentials: [
      { rank: 1, icd_code: "J18.9", description: "Community-Acquired Pneumonia", description_th: "ปอดอักเสบชุมชน", probability: 0.87, reasoning: "พบอาการ 5 รายการที่สอดคล้องกับ CAP", evidence: ["อาการ: fever (น้ำหนัก 0.8)", "อาการ: cough (น้ำหนัก 0.9)", "อาการ: dyspnea (น้ำหนัก 0.7)", "อาการ: sputum (น้ำหนัก 0.8)", "อาการ: tachypnea (น้ำหนัก 0.6)", "ปัจจัยเสี่ยง: copd", "อายุ ≥ 65 ปี", "ผลตรวจ: WBC ↑"], cpg_reference: "Thai CPG CAP 2023" },
      { rank: 2, icd_code: "A41.9", description: "Sepsis", description_th: "ภาวะติดเชื้อในกระแสเลือด", probability: 0.52, reasoning: "พบอาการ 3 รายการที่สอดคล้อง", evidence: ["อาการ: fever", "อาการ: tachypnea", "ผลตรวจ: Procalcitonin ↑↑"], cpg_reference: "Surviving Sepsis 2021" },
      { rank: 3, icd_code: "N17.9", description: "Acute Kidney Injury", description_th: "ไตวายเฉียบพลัน", probability: 0.41, reasoning: "Cr สูงขึ้น", evidence: ["ผลตรวจ: Creatinine 1.8 (↑)", "ปัจจัยเสี่ยง: diabetes"], cpg_reference: "KDIGO AKI 2012" },
    ],
    primary_disease_group: "CAP",
    confidence_note: "คำนวณจาก GraphRAG knowledge graph traversal",
  },
  "ENC-2567-0003": {
    differentials: [
      { rank: 1, icd_code: "I50.1", description: "Left Ventricular Failure", description_th: "หัวใจห้องล่างซ้ายล้มเหลว", probability: 0.91, reasoning: "อาการครบถ้วนสำหรับ ADHF", evidence: ["อาการ: dyspnea", "อาการ: orthopnea", "อาการ: edema", "ผลตรวจ: BNP 1850 ↑↑↑", "ปัจจัยเสี่ยง: hypertension, cad, diabetes", "อายุ ≥ 65 ปี"], cpg_reference: "Thai CPG HF 2023" },
      { rank: 2, icd_code: "I50.9", description: "Heart Failure, Unspecified", description_th: "ภาวะหัวใจล้มเหลว", probability: 0.78, reasoning: "HF features present", evidence: ["อาการ: dyspnea", "อาการ: edema", "ผลตรวจ: BNP ↑"], cpg_reference: "ESC HF 2023" },
    ],
    primary_disease_group: "HF",
    confidence_note: "คำนวณจาก GraphRAG knowledge graph traversal",
  },
};

const DEMO_ORDERS: Record<string, OrderSuggestionResponse> = {
  "CAP": {
    orders: [
      { category: "LAB", code: "CBC", display_name: "Complete Blood Count", priority: "ESSENTIAL", rationale: "ประเมินการติดเชื้อ (WBC, Neutrophil)", cpg_source: "Thai CPG CAP 2023" },
      { category: "LAB", code: "Blood_culture", display_name: "Blood Culture x2", priority: "ESSENTIAL", rationale: "หา causative organism (ก่อนให้ ATB)", cpg_source: null },
      { category: "LAB", code: "Procalcitonin", display_name: "Procalcitonin", priority: "RECOMMENDED", rationale: "แยก bacterial vs viral", cpg_source: null },
      { category: "IMAGING", code: "CXR", display_name: "Chest X-ray PA upright", priority: "ESSENTIAL", rationale: "ยืนยัน infiltrate, ประเมิน severity", cpg_source: null },
      { category: "MEDICATION", code: "Ceftriaxone", display_name: "Ceftriaxone 2g IV q24h", priority: "ESSENTIAL", rationale: "Empiric ATB สำหรับ CAP", cpg_source: "Thai CPG CAP 2023" },
      { category: "MEDICATION", code: "Azithromycin", display_name: "Azithromycin 500mg IV/PO qd", priority: "ESSENTIAL", rationale: "Atypical coverage", cpg_source: "Thai CPG CAP 2023" },
      { category: "NURSING", code: "O2_monitor", display_name: "SpO2 monitoring q4h", priority: "ESSENTIAL", rationale: "เฝ้าระวัง respiratory failure", cpg_source: null },
      { category: "DIET", code: "soft_diet", display_name: "อาหารอ่อน (Soft diet)", priority: "RECOMMENDED", rationale: "ง่ายต่อการรับประทาน", cpg_source: null },
    ],
    disease_group: "CAP",
    personalization_notes: ["ผู้สูงอายุ ≥65 ปี: ปรับขนาดยาตามไต", "Cr=1.8: หลีกเลี่ยงยาทำลายไต, ปรับขนาด"],
  },
  "HF": {
    orders: [
      { category: "LAB", code: "BNP", display_name: "BNP / NT-proBNP", priority: "ESSENTIAL", rationale: "ยืนยันและประเมิน severity ของ HF", cpg_source: null },
      { category: "IMAGING", code: "Echo", display_name: "Echocardiogram", priority: "ESSENTIAL", rationale: "ประเมิน EF, valvular disease", cpg_source: null },
      { category: "IMAGING", code: "ECG", display_name: "12-Lead ECG", priority: "ESSENTIAL", rationale: "ดู arrhythmia, ischemia", cpg_source: null },
      { category: "MEDICATION", code: "Furosemide", display_name: "Furosemide 40mg IV", priority: "ESSENTIAL", rationale: "ลด fluid overload", cpg_source: "ESC HF 2023" },
      { category: "MEDICATION", code: "Enalapril", display_name: "Enalapril 5mg PO BID", priority: "ESSENTIAL", rationale: "ACEi for HFrEF", cpg_source: "ESC HF 2023" },
      { category: "NURSING", code: "daily_weight", display_name: "ชั่งน้ำหนักทุกเช้า", priority: "ESSENTIAL", rationale: "ติดตาม fluid balance", cpg_source: null },
      { category: "DIET", code: "low_salt", display_name: "อาหารจำกัดเกลือ <2g Na/วัน", priority: "ESSENTIAL", rationale: "ลด fluid retention", cpg_source: null },
    ],
    disease_group: "HF",
    personalization_notes: ["ผู้สูงอายุ ≥65 ปี: ปรับขนาดยาตามไต"],
  },
};

const DEMO_ADMISSION: Record<string, AdmissionDecisionResponse> = {
  "ENC-2567-0001": {
    recommendation: "WARD", risk_level: "HIGH",
    risk_scores: [
      { tool_name: "CURB-65", score: 3, max_score: 5, components: { "Confusion": 0, "Urea>7": 1, "RR≥30": 0, "BP<90/60": 0, "Age≥65": 1 }, interpretation: "High risk", mortality_risk: "14%" },
      { tool_name: "qSOFA", score: 1, max_score: 3, components: { "RR≥22": 1, "SBP≤100": 0, "Altered mentation": 0 }, interpretation: "Low risk", mortality_risk: "<10%" },
    ],
    reasoning: "CURB-65 score 3 — ควรรับไว้ในหอผู้ป่วย, qSOFA ยังไม่ถึงเกณฑ์ sepsis", suggested_ward: "อายุรกรรม (Medicine Ward)",
  },
  "ENC-2567-0003": {
    recommendation: "ICU", risk_level: "CRITICAL",
    risk_scores: [
      { tool_name: "qSOFA", score: 2, max_score: 3, components: { "RR≥22": 1, "SBP≤100": 0, "Altered mentation": 1 }, interpretation: "High risk — evaluate for sepsis", mortality_risk: ">10%" },
    ],
    reasoning: "BNP สูงมาก (1850), SpO2 ต่ำ (88%), ต้องการ O2 support — ควรรับ ICU/CCU", suggested_ward: "ICU / CCU",
  },
};

const DEMO_CHART: Record<string, ChartScoreResponse> = {
  "ENC-2567-0001": {
    encounter_id: "ENC-2567-0001", total_score: 68.2, grade: "C",
    breakdown: [
      { category: "DIAGNOSIS", score: 55, max_score: 100, weight: 0.3, items_found: 35, items_expected: 64 },
      { category: "PROCEDURE", score: 100, max_score: 100, weight: 0.2, items_found: 20, items_expected: 20 },
      { category: "CONSISTENCY", score: 57, max_score: 100, weight: 0.25, items_found: 20, items_expected: 35 },
      { category: "DOCUMENTATION", score: 66, max_score: 100, weight: 0.25, items_found: 20, items_expected: 30 },
    ],
    gaps: [
      { rule_id: "DX-02", category: "DIAGNOSIS", description: "SDx: Hypertension (if BP↑) — BP 145/88 แต่ไม่ได้ลง I10", severity: "WARNING", suggested_action: "ADD_SDX", suggested_code: "I10" },
      { rule_id: "DX-04", category: "DIAGNOSIS", description: "SDx: AKI (if Cr↑) — Cr 1.8 แต่ไม่ได้ลง N17.9", severity: "CRITICAL", suggested_action: "ADD_SDX", suggested_code: "N17.9" },
      { rule_id: "DX-05", category: "DIAGNOSIS", description: "SDx: Anemia (if Hb↓) — Hb 11.2 ไม่ได้ลง D64.9", severity: "WARNING", suggested_action: "ADD_SDX", suggested_code: "D64.9" },
      { rule_id: "DX-06", category: "DIAGNOSIS", description: "SDx: Hypokalemia (K 3.2) — ไม่ได้ลง E87.6", severity: "WARNING", suggested_action: "ADD_SDX", suggested_code: "E87.6" },
    ],
    evaluated_at: new Date().toISOString(),
  },
};

const DEMO_CODES: Record<string, CodeSuggestionResponse> = {
  "ENC-2567-0001": {
    encounter_id: "ENC-2567-0001",
    suggestions: [
      { id: 1, icd_code: "N17.9", description: "Acute Kidney Injury", dx_type: "SDx", confidence: 0.85, evidence: ["Creatinine = 1.8 (≥ 1.5)", "มี Progress Note สนับสนุน", "มีการสั่งยาที่สอดคล้อง"], rw_impact: 1.2345, status: "PENDING" },
      { id: 2, icd_code: "E87.6", description: "Hypokalemia", dx_type: "SDx", confidence: 0.90, evidence: ["Potassium = 3.2 (< 3.5)", "มี Progress Note สนับสนุน"], rw_impact: 0.55, status: "PENDING" },
      { id: 3, icd_code: "A41.9", description: "Sepsis", dx_type: "SDx", confidence: 0.80, evidence: ["Procalcitonin = 4.5 (> 2.0)", "มี Progress Note สนับสนุน", "มีการสั่งยาที่สอดคล้อง"], rw_impact: 2.1543, status: "PENDING" },
      { id: 4, icd_code: "D64.9", description: "Anemia, Unspecified", dx_type: "SDx", confidence: 0.75, evidence: ["Hemoglobin = 9.5 (< 10)"], rw_impact: 0.50, status: "PENDING" },
    ],
    rw_before: 0.8956, rw_after: 5.3344, rw_delta: 4.4388, revenue_impact_thb: 53265.6, drg: null,
  },
};

const categoryIcons: Record<string, string> = { LAB: "🧪", IMAGING: "📷", MEDICATION: "💊", NURSING: "👩‍⚕️", DIET: "🍽️" };

export default function PatientPage() {
  const params = useParams();
  const encId = params.id as string;
  const enc = DEMO_ENCOUNTERS[encId] ?? DEMO_ENCOUNTERS["ENC-2567-0001"];
  const prediag = DEMO_PREDIAG[encId] ?? DEMO_PREDIAG["ENC-2567-0001"];
  const group = prediag?.primary_disease_group ?? "CAP";
  const orders = DEMO_ORDERS[group] ?? DEMO_ORDERS["CAP"];
  const admission = DEMO_ADMISSION[encId] ?? DEMO_ADMISSION["ENC-2567-0001"];
  const chart = DEMO_CHART[encId] ?? DEMO_CHART["ENC-2567-0001"];
  const codes = DEMO_CODES[encId] ?? DEMO_CODES["ENC-2567-0001"];
  const [acceptedIds, setAcceptedIds] = useState<Set<number>>(new Set());

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Patient Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">{enc.patient.name}</h1>
            <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
              <span>HN: {enc.patient.hn}</span>
              <span>•</span>
              <span>{enc.patient.age} ปี / {enc.patient.sex === "M" ? "ชาย" : "หญิง"}</span>
              <span>•</span>
              <span>{enc.ward}</span>
              <span>•</span>
              <span>LOS: {enc.los} วัน</span>
            </div>
            <p className="mt-1 text-sm"><strong>Chief Complaint:</strong> {enc.cc}</p>
            {enc.patient.allergies.length > 0 && (
              <div className="mt-1 flex items-center gap-1">
                <Badge className="bg-red-100 text-red-700 text-[10px]">⚠️ แพ้ยา</Badge>
                {enc.patient.allergies.map(a => <Badge key={a} variant="destructive" className="text-[10px]">{a}</Badge>)}
              </div>
            )}
          </div>
          <Badge className={cn("text-sm", getStatusColor(enc.status))}>
            {enc.status === "ACTIVE" ? "กำลังรักษา" : "จำหน่ายแล้ว"}
          </Badge>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="cds" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="cds">🩺 CDS วินิจฉัย</TabsTrigger>
            <TabsTrigger value="orders">📋 สั่งการรักษา</TabsTrigger>
            <TabsTrigger value="chart">📊 Chart Score</TabsTrigger>
            <TabsTrigger value="coding">🔢 Code Suggestion</TabsTrigger>
          </TabsList>

          {/* CDS Tab */}
          <TabsContent value="cds" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-2">
              {/* Differential Diagnosis */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">🎯 Differential Diagnosis</CardTitle>
                  <CardDescription>{prediag?.confidence_note}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {prediag?.differentials.map((dx) => (
                    <div key={dx.rank} className="rounded-lg border p-3 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-white text-xs font-bold">
                            {dx.rank}
                          </span>
                          <div>
                            <p className="font-medium text-sm">{dx.description}</p>
                            <p className="text-xs text-muted-foreground">{dx.description_th}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="font-mono text-xs">{dx.icd_code}</Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={dx.probability * 100}
                          className="flex-1 h-3"
                          indicatorClassName={dx.probability >= 0.7 ? "bg-green-500" : dx.probability >= 0.4 ? "bg-yellow-500" : "bg-gray-400"}
                        />
                        <span className={cn("text-sm font-bold", dx.probability >= 0.7 ? "text-green-600" : dx.probability >= 0.4 ? "text-yellow-600" : "text-gray-500")}>
                          {(dx.probability * 100).toFixed(0)}%
                        </span>
                      </div>
                      <details className="text-xs">
                        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">หลักฐานสนับสนุน ({dx.evidence.length})</summary>
                        <ul className="mt-1 space-y-0.5 pl-4 list-disc text-muted-foreground">
                          {dx.evidence.map((e, i) => <li key={i}>{e}</li>)}
                        </ul>
                        {dx.cpg_reference && <p className="mt-1 text-primary">📖 {dx.cpg_reference}</p>}
                      </details>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Admission Decision */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">🏥 Admission Decision</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className={cn("rounded-lg p-4 text-center", getSeverityColor(admission.risk_level))}>
                    <p className="text-xs font-medium uppercase">คำแนะนำ</p>
                    <p className="text-2xl font-bold">{admission.recommendation}</p>
                    <p className="text-sm mt-1">{admission.suggested_ward}</p>
                  </div>

                  {admission.risk_scores.map((rs) => (
                    <div key={rs.tool_name} className="rounded-lg border p-3 space-y-2">
                      <div className="flex justify-between items-center">
                        <h4 className="font-semibold text-sm">{rs.tool_name}</h4>
                        <div className="text-right">
                          <span className="text-2xl font-bold">{rs.score}</span>
                          <span className="text-sm text-muted-foreground">/{rs.max_score}</span>
                        </div>
                      </div>
                      <Progress
                        value={(rs.score / rs.max_score) * 100}
                        className="h-3"
                        indicatorClassName={rs.score / rs.max_score >= 0.6 ? "bg-red-500" : rs.score / rs.max_score >= 0.4 ? "bg-yellow-500" : "bg-green-500"}
                      />
                      <div className="grid grid-cols-2 gap-1 text-xs">
                        {Object.entries(rs.components).map(([k, v]) => (
                          <div key={k} className="flex justify-between">
                            <span className="text-muted-foreground">{k}</span>
                            <span className={v > 0 ? "text-red-600 font-bold" : "text-green-600"}>{v > 0 ? "✓" : "✗"}</span>
                          </div>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {rs.interpretation} • Mortality: {rs.mortality_risk}
                      </p>
                    </div>
                  ))}

                  <p className="text-sm text-muted-foreground italic">{admission.reasoning}</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">📋 CPG-Compliant Order Suggestions</CardTitle>
                <CardDescription>Disease Group: {orders.disease_group} | ตาม CPG แห่งประเทศไทย</CardDescription>
              </CardHeader>
              <CardContent>
                {orders.personalization_notes.length > 0 && (
                  <div className="mb-4 rounded-lg bg-blue-50 dark:bg-blue-950 p-3 space-y-1">
                    <p className="text-sm font-medium text-blue-700 dark:text-blue-300">⚡ Personalization Notes:</p>
                    {orders.personalization_notes.map((n, i) => (
                      <p key={i} className="text-xs text-blue-600 dark:text-blue-400">• {n}</p>
                    ))}
                  </div>
                )}

                {["ESSENTIAL", "RECOMMENDED", "OPTIONAL"].map(priority => {
                  const items = orders.orders.filter(o => o.priority === priority);
                  if (items.length === 0) return null;
                  return (
                    <div key={priority} className="mb-4">
                      <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                        <Badge className={getPriorityColor(priority)}>{priority}</Badge>
                        <span className="text-muted-foreground text-xs">({items.length} รายการ)</span>
                      </h3>
                      <div className="space-y-2">
                        {items.map((o, i) => (
                          <div key={i} className="flex items-start gap-3 rounded-lg border p-3 hover:bg-muted/50 transition-colors">
                            <input type="checkbox" defaultChecked={priority === "ESSENTIAL"} className="mt-1 h-4 w-4 rounded border-gray-300" />
                            <span className="text-lg">{categoryIcons[o.category] ?? "📋"}</span>
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-[10px]">{o.category}</Badge>
                                <span className="text-sm font-medium">{o.display_name}</span>
                              </div>
                              <p className="text-xs text-muted-foreground mt-0.5">{o.rationale}</p>
                              {o.cpg_source && <p className="text-[10px] text-primary mt-0.5">📖 {o.cpg_source}</p>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chart Completeness Tab */}
          <TabsContent value="chart" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-3">
              {/* Score Circle */}
              <Card className="lg:col-span-1">
                <CardContent className="flex flex-col items-center justify-center p-6">
                  <div className="relative h-40 w-40">
                    <svg className="h-40 w-40 -rotate-90" viewBox="0 0 160 160">
                      <circle cx="80" cy="80" r="70" fill="none" stroke="currentColor" strokeWidth="12" className="text-muted" />
                      <circle
                        cx="80" cy="80" r="70" fill="none" strokeWidth="12"
                        strokeDasharray={`${(chart.total_score / 100) * 440} 440`}
                        strokeLinecap="round"
                        className={chart.total_score >= 75 ? "stroke-green-500" : chart.total_score >= 60 ? "stroke-yellow-500" : "stroke-red-500"}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className={cn("text-3xl font-bold", getScoreColor(chart.total_score))}>{chart.total_score}%</span>
                      <span className="text-lg font-semibold text-muted-foreground">Grade {chart.grade}</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-center text-muted-foreground">Chart Completeness Score</p>
                </CardContent>
              </Card>

              {/* Category Breakdown */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg">📊 Category Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {chart.breakdown.map((b) => (
                    <div key={b.category} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{b.category}</span>
                        <span className="text-muted-foreground">
                          {b.score.toFixed(0)}% (weight: {(b.weight * 100).toFixed(0)}%)
                        </span>
                      </div>
                      <Progress
                        value={b.score}
                        className="h-3"
                        indicatorClassName={b.score >= 80 ? "bg-green-500" : b.score >= 60 ? "bg-yellow-500" : "bg-red-500"}
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Gaps */}
            {chart.gaps.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">⚠️ Documentation Gaps ({chart.gaps.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {chart.gaps.map((g, i) => (
                      <div key={i} className={cn("flex items-start gap-3 rounded-lg border p-3", g.severity === "CRITICAL" ? "border-red-200 bg-red-50 dark:bg-red-950" : "border-yellow-200 bg-yellow-50 dark:bg-yellow-950")}>
                        <span className="text-lg">{g.severity === "CRITICAL" ? "🔴" : "🟡"}</span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-[10px]">{g.rule_id}</Badge>
                            <Badge variant="outline" className="text-[10px]">{g.category}</Badge>
                          </div>
                          <p className="text-sm mt-0.5">{g.description}</p>
                          {g.suggested_code && (
                            <p className="text-xs text-primary mt-1">💡 แนะนำเพิ่ม: {g.suggested_code}</p>
                          )}
                        </div>
                        <Badge className={getSeverityColor(g.severity)}>{g.severity}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Code Suggestion Tab */}
          <TabsContent value="coding" className="space-y-4">
            {/* RW Impact Summary */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">RW ปัจจุบัน</p>
                  <p className="text-2xl font-bold">{codes.rw_before.toFixed(4)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">RW หลังเพิ่มรหัส</p>
                  <p className="text-2xl font-bold text-green-600">{codes.rw_after.toFixed(4)}</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">RW Delta</p>
                  <p className="text-2xl font-bold text-primary">+{codes.rw_delta.toFixed(4)}</p>
                </CardContent>
              </Card>
              <Card className="bg-green-50 dark:bg-green-950 border-green-200">
                <CardContent className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Revenue Impact</p>
                  <p className="text-2xl font-bold text-green-600">{formatCurrency(codes.revenue_impact_thb)}</p>
                </CardContent>
              </Card>
            </div>

            {/* Suggestions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">🔢 AI Code Suggestions</CardTitle>
                <CardDescription>รหัส ICD-10 ที่แนะนำเพิ่มเติมตามผลตรวจและเอกสาร</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {codes.suggestions.map((s) => (
                    <div key={s.id} className={cn("rounded-lg border p-4 transition-colors", acceptedIds.has(s.id) ? "bg-green-50 dark:bg-green-950 border-green-300" : "hover:bg-muted/50")}>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="font-mono">{s.icd_code}</Badge>
                            <span className="font-medium">{s.description}</span>
                            <Badge className="text-[10px] bg-gray-100 text-gray-600">{s.dx_type}</Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-muted-foreground">Confidence:</span>
                            <Progress value={s.confidence * 100} className="w-24 h-2" indicatorClassName="bg-primary" />
                            <span className="text-sm font-medium">{(s.confidence * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>RW Impact: +{s.rw_impact.toFixed(4)}</span>
                            <span>•</span>
                            <span>Revenue: {formatCurrency(s.rw_impact * 12000)}</span>
                          </div>
                          <details className="text-xs">
                            <summary className="cursor-pointer text-muted-foreground hover:text-foreground">หลักฐาน ({s.evidence.length})</summary>
                            <ul className="mt-1 pl-4 list-disc text-muted-foreground space-y-0.5">
                              {s.evidence.map((e, i) => <li key={i}>{e}</li>)}
                            </ul>
                          </details>
                        </div>
                        <div className="flex gap-2">
                          {acceptedIds.has(s.id) ? (
                            <Badge className="bg-green-100 text-green-700">✓ ACCEPTED</Badge>
                          ) : (
                            <>
                              <Button size="sm" onClick={() => setAcceptedIds(prev => new Set([...prev, s.id]))}>✓ Accept</Button>
                              <Button size="sm" variant="outline">✗ Reject</Button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
