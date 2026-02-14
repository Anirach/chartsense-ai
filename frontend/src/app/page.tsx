"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn, getStatusColor, getScoreColor, formatCurrency } from "@/lib/utils";
import type { Patient, Encounter } from "@/types";

// Demo data (used when API is not available)
const DEMO_PATIENTS: (Patient & { encounters: Encounter[] })[] = [
  { id: 1, hn: "HN-640001", name: "นายสมชาย ใจดี", age: 72, sex: "M", pmh: ["hypertension", "diabetes", "copd"], allergies: ["Penicillin"],
    encounters: [{ id: 1, encounter_id: "ENC-2567-0001", patient_id: 1, admit_date: "2026-02-09", dc_date: null, ward: "อายุรกรรมชาย 1", los: 5, status: "ACTIVE", chief_complaint: "ไข้สูง 3 วัน ไอมีเสมหะเหลืองข้น หอบเหนื่อย" }] },
  { id: 2, hn: "HN-640002", name: "นางสมหญิง รักษ์สุข", age: 65, sex: "F", pmh: ["diabetes", "ckd"], allergies: [],
    encounters: [{ id: 2, encounter_id: "ENC-2567-0002", patient_id: 2, admit_date: "2026-02-11", dc_date: null, ward: "อายุรกรรมหญิง 1", los: 3, status: "ACTIVE", chief_complaint: "อ่อนเพลีย คลื่นไส้ 2 วัน ปัสสาวะน้อยลง" }] },
  { id: 3, hn: "HN-640003", name: "นายประเสริฐ มั่นคง", age: 78, sex: "M", pmh: ["hypertension", "cad", "diabetes"], allergies: ["Sulfa"],
    encounters: [{ id: 3, encounter_id: "ENC-2567-0003", patient_id: 3, admit_date: "2026-02-07", dc_date: null, ward: "CCU", los: 7, status: "ACTIVE", chief_complaint: "หอบเหนื่อย นอนราบไม่ได้ 3 วัน ขาบวม 2 ข้าง" }] },
  { id: 4, hn: "HN-640005", name: "นายบุญเลิศ แก้วมณี", age: 80, sex: "M", pmh: ["hypertension", "cad", "hf"], allergies: ["NSAIDs"],
    encounters: [{ id: 4, encounter_id: "ENC-2567-0004", patient_id: 5, admit_date: "2026-02-10", dc_date: null, ward: "อายุรกรรมชาย 2", los: 4, status: "ACTIVE", chief_complaint: "เหนื่อยง่ายขึ้น 1 สัปดาห์ ขาบวม น้ำหนักขึ้น 3 กก." }] },
  { id: 5, hn: "HN-640007", name: "นายวิชัย สุขสันต์", age: 68, sex: "M", pmh: ["hypertension", "smoking"], allergies: [],
    encounters: [{ id: 5, encounter_id: "ENC-2567-0005", patient_id: 7, admit_date: "2026-02-11", dc_date: null, ward: "อายุรกรรมชาย 1", los: 3, status: "ACTIVE", chief_complaint: "ไข้ ไอ 5 วัน เจ็บหน้าอกเวลาหายใจลึก" }] },
  { id: 6, hn: "HN-640004", name: "นางวิภา ศรีสวัสดิ์", age: 58, sex: "F", pmh: ["diabetes", "dyslipidemia"], allergies: [],
    encounters: [{ id: 6, encounter_id: "ENC-2567-0006", patient_id: 4, admit_date: "2026-02-12", dc_date: null, ward: "อายุรกรรมหญิง 2", los: 2, status: "ACTIVE", chief_complaint: "แผลที่เท้าซ้าย 2 สัปดาห์ น้ำตาลคุมไม่ได้" }] },
  { id: 7, hn: "HN-640008", name: "นางนวล จันทร์เพ็ญ", age: 70, sex: "F", pmh: ["hypertension", "diabetes", "valvular_disease"], allergies: ["Iodine"],
    encounters: [{ id: 7, encounter_id: "ENC-2567-0007", patient_id: 8, admit_date: "2026-02-08", dc_date: "2026-02-13", ward: "อายุรกรรมหญิง 1", los: 6, status: "DISCHARGED", chief_complaint: "หอบเหนื่อย นอนราบไม่ได้" }] },
  { id: 8, hn: "HN-640009", name: "นายธนากร เพชรรัตน์", age: 55, sex: "M", pmh: ["diabetes", "obesity"], allergies: [],
    encounters: [{ id: 8, encounter_id: "ENC-2567-0008", patient_id: 9, admit_date: "2026-02-10", dc_date: null, ward: "อายุรกรรมชาย 2", los: 4, status: "ACTIVE", chief_complaint: "ซึม สับสน น้ำตาลสูงมาก" }] },
  { id: 9, hn: "HN-640010", name: "นางสาวอรุณี วงศ์สกุล", age: 62, sex: "F", pmh: ["hypertension", "copd"], allergies: ["Aspirin"],
    encounters: [{ id: 9, encounter_id: "ENC-2567-0009", patient_id: 10, admit_date: "2026-02-10", dc_date: null, ward: "อายุรกรรมหญิง 2", los: 4, status: "ACTIVE", chief_complaint: "ไข้สูง ไอ หอบ 2 วัน" }] },
];

const DEMO_CHART_SCORES: Record<string, number> = {
  "ENC-2567-0001": 68,
  "ENC-2567-0002": 82,
  "ENC-2567-0003": 75,
  "ENC-2567-0004": 60,
  "ENC-2567-0005": 55,
  "ENC-2567-0006": 72,
  "ENC-2567-0007": 90,
  "ENC-2567-0008": 78,
  "ENC-2567-0009": 45,
};

const DEMO_PENDING_CODES: Record<string, number> = {
  "ENC-2567-0001": 4,
  "ENC-2567-0002": 2,
  "ENC-2567-0003": 3,
  "ENC-2567-0004": 1,
  "ENC-2567-0005": 2,
  "ENC-2567-0008": 3,
  "ENC-2567-0009": 5,
};

const diseaseGroupLabels: Record<string, { label: string; color: string }> = {
  "CAP": { label: "CAP", color: "bg-orange-100 text-orange-700" },
  "DM": { label: "DM", color: "bg-purple-100 text-purple-700" },
  "HF": { label: "HF", color: "bg-blue-100 text-blue-700" },
};

function getDiseaseGroup(cc: string): string {
  if (cc.includes("ไข้") || cc.includes("ไอ") || cc.includes("ปอด")) return "CAP";
  if (cc.includes("น้ำตาล") || cc.includes("เบาหวาน") || cc.includes("แผล") || cc.includes("ซึม")) return "DM";
  if (cc.includes("หอบ") || cc.includes("บวม") || cc.includes("หัวใจ") || cc.includes("เหนื่อย")) return "HF";
  return "CAP";
}

export default function DashboardPage() {
  const activePatients = DEMO_PATIENTS.filter(p => p.encounters.some(e => e.status === "ACTIVE"));
  const totalPending = Object.values(DEMO_PENDING_CODES).reduce((a, b) => a + b, 0);
  const avgScore = Math.round(Object.values(DEMO_CHART_SCORES).reduce((a, b) => a + b, 0) / Object.values(DEMO_CHART_SCORES).length);
  const criticalPatients = DEMO_PATIENTS.filter(p => {
    const enc = p.encounters[0];
    const score = DEMO_CHART_SCORES[enc.encounter_id] ?? 100;
    return score < 60 && enc.status === "ACTIVE";
  });

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">แดชบอร์ด</h1>
          <p className="text-muted-foreground">ภาพรวมระบบสนับสนุนการตัดสินใจทางคลินิก</p>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ผู้ป่วย Active</CardTitle>
              <span className="text-2xl">🏥</span>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{activePatients.length}</div>
              <p className="text-xs text-muted-foreground">ราย กำลังรักษาตัว</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Chart Score เฉลี่ย</CardTitle>
              <span className="text-2xl">📋</span>
            </CardHeader>
            <CardContent>
              <div className={cn("text-3xl font-bold", getScoreColor(avgScore))}>{avgScore}%</div>
              <Progress value={avgScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">รหัสรอตรวจสอบ</CardTitle>
              <span className="text-2xl">🔍</span>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">{totalPending}</div>
              <p className="text-xs text-muted-foreground">รายการ Pending Review</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ผู้ป่วยเสี่ยงสูง</CardTitle>
              <span className="text-2xl">⚠️</span>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">{criticalPatients.length}</div>
              <p className="text-xs text-muted-foreground">ราย Chart Score &lt; 60%</p>
            </CardContent>
          </Card>
        </div>

        {/* Patient List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">รายชื่อผู้ป่วย</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">HN</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">ชื่อ-สกุล</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">อายุ/เพศ</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">Ward</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">กลุ่มโรค</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">Chart Score</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">รหัสรอ</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground">สถานะ</th>
                    <th className="text-left py-3 px-2 font-medium text-muted-foreground"></th>
                  </tr>
                </thead>
                <tbody>
                  {DEMO_PATIENTS.map((p) => {
                    const enc = p.encounters[0];
                    const score = DEMO_CHART_SCORES[enc.encounter_id] ?? 0;
                    const pending = DEMO_PENDING_CODES[enc.encounter_id] ?? 0;
                    const group = getDiseaseGroup(enc.chief_complaint ?? "");
                    const groupInfo = diseaseGroupLabels[group] ?? { label: group, color: "bg-gray-100 text-gray-700" };

                    return (
                      <tr key={p.id} className="border-b hover:bg-muted/50 transition-colors">
                        <td className="py-3 px-2 font-mono text-xs">{p.hn}</td>
                        <td className="py-3 px-2 font-medium">{p.name}</td>
                        <td className="py-3 px-2">{p.age} ปี / {p.sex === "M" ? "ชาย" : "หญิง"}</td>
                        <td className="py-3 px-2 text-xs">{enc.ward}</td>
                        <td className="py-3 px-2">
                          <Badge className={cn("text-[10px]", groupInfo.color)}>{groupInfo.label}</Badge>
                        </td>
                        <td className="py-3 px-2">
                          <div className="flex items-center gap-2">
                            <Progress value={score} className="w-16 h-2" indicatorClassName={score >= 75 ? "bg-green-500" : score >= 60 ? "bg-yellow-500" : "bg-red-500"} />
                            <span className={cn("text-xs font-medium", getScoreColor(score))}>{score}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-2">
                          {pending > 0 && <Badge className="bg-yellow-100 text-yellow-700 text-[10px]">{pending} รายการ</Badge>}
                        </td>
                        <td className="py-3 px-2">
                          <Badge className={cn("text-[10px]", getStatusColor(enc.status))}>{enc.status === "ACTIVE" ? "กำลังรักษา" : "จำหน่ายแล้ว"}</Badge>
                        </td>
                        <td className="py-3 px-2">
                          <Link
                            href={`/patients/${enc.encounter_id}`}
                            className="text-primary text-xs hover:underline font-medium"
                          >
                            ดูรายละเอียด →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Disease Group Summary */}
        <div className="grid gap-4 md:grid-cols-3">
          {Object.entries(diseaseGroupLabels).map(([key, info]) => {
            const count = DEMO_PATIENTS.filter(p => getDiseaseGroup(p.encounters[0].chief_complaint ?? "") === key && p.encounters[0].status === "ACTIVE").length;
            return (
              <Card key={key}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Badge className={cn("mb-2", info.color)}>{info.label}</Badge>
                      <p className="text-2xl font-bold">{count}</p>
                      <p className="text-xs text-muted-foreground">ราย Active</p>
                    </div>
                    <div className="text-4xl">
                      {key === "CAP" ? "🫁" : key === "DM" ? "💉" : "❤️"}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
