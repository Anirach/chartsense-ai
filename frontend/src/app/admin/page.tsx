"use client";

import React from "react";
import AppShell from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const DEMO_RULES = [
  { rule_id: "DX-01", category: "DIAGNOSIS", name: "PDx ต้องมีอย่างน้อย 1 รายการ", weight: 15, active: true },
  { rule_id: "DX-02", category: "DIAGNOSIS", name: "SDx: Hypertension (if BP↑)", weight: 8, active: true },
  { rule_id: "DX-03", category: "DIAGNOSIS", name: "SDx: DM (if FBS↑)", weight: 8, active: true },
  { rule_id: "DX-04", category: "DIAGNOSIS", name: "SDx: AKI (if Cr↑)", weight: 10, active: true },
  { rule_id: "DX-05", category: "DIAGNOSIS", name: "SDx: Anemia (if Hb↓)", weight: 6, active: true },
  { rule_id: "DX-06", category: "DIAGNOSIS", name: "SDx: Hypokalemia (if K↓)", weight: 7, active: true },
  { rule_id: "DX-07", category: "DIAGNOSIS", name: "SDx: Hyperkalemia (if K↑)", weight: 7, active: true },
  { rule_id: "DX-08", category: "DIAGNOSIS", name: "SDx: Sepsis (if qSOFA≥2)", weight: 12, active: true },
  { rule_id: "PR-01", category: "PROCEDURE", name: "ต้องลง Procedure ถ้ามีหัตถการ", weight: 10, active: true },
  { rule_id: "PR-02", category: "PROCEDURE", name: "Ventilator procedure code", weight: 10, active: true },
  { rule_id: "CO-01", category: "CONSISTENCY", name: "Dx สอดคล้องกับ Lab", weight: 10, active: true },
  { rule_id: "CO-02", category: "CONSISTENCY", name: "Dx สอดคล้องกับ Medication", weight: 8, active: true },
  { rule_id: "CO-03", category: "CONSISTENCY", name: "PDx ตรง Chief Complaint", weight: 7, active: true },
  { rule_id: "CO-04", category: "CONSISTENCY", name: "LOS สอดคล้องกับ Severity", weight: 5, active: true },
  { rule_id: "CO-05", category: "CONSISTENCY", name: "ลำดับ Dx ถูกต้อง", weight: 5, active: true },
  { rule_id: "DO-01", category: "DOCUMENTATION", name: "Progress Note มีครบทุกวัน", weight: 8, active: true },
  { rule_id: "DO-02", category: "DOCUMENTATION", name: "Discharge Summary มี", weight: 8, active: true },
  { rule_id: "DO-03", category: "DOCUMENTATION", name: "Vital Signs บันทึกครบ", weight: 5, active: true },
  { rule_id: "DO-04", category: "DOCUMENTATION", name: "Allergy ระบุในแฟ้ม", weight: 4, active: true },
  { rule_id: "DO-05", category: "DOCUMENTATION", name: "Informed Consent บันทึก", weight: 5, active: true },
];

const DEMO_TEMPLATES = [
  { template_id: "CPG-CAP-2023", disease_group: "CAP", name: "Thai CPG: Community-Acquired Pneumonia 2023", orders_count: 13, version: "1.0" },
  { template_id: "CPG-DM-2023", disease_group: "DM", name: "Thai CPG: DM Complications Management 2023", orders_count: 12, version: "1.0" },
  { template_id: "CPG-HF-2023", disease_group: "HF", name: "Thai CPG: Heart Failure Management 2023", orders_count: 15, version: "1.0" },
];

const catColors: Record<string, string> = {
  DIAGNOSIS: "bg-blue-100 text-blue-700",
  PROCEDURE: "bg-purple-100 text-purple-700",
  CONSISTENCY: "bg-orange-100 text-orange-700",
  DOCUMENTATION: "bg-green-100 text-green-700",
};

export default function AdminPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">ตั้งค่าระบบ</h1>
          <p className="text-muted-foreground">จัดการกฎ, เทมเพลต CPG, และการตั้งค่าระบบ</p>
        </div>

        <Tabs defaultValue="rules">
          <TabsList>
            <TabsTrigger value="rules">📏 กฎ Chart Completeness</TabsTrigger>
            <TabsTrigger value="templates">📋 CPG Templates</TabsTrigger>
            <TabsTrigger value="settings">⚙️ ตั้งค่า</TabsTrigger>
          </TabsList>

          <TabsContent value="rules" className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-muted-foreground">{DEMO_RULES.length} กฎทั้งหมด</p>
              <Button size="sm">+ เพิ่มกฎใหม่</Button>
            </div>
            <Card>
              <CardContent className="p-0">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left py-3 px-4 font-medium">Rule ID</th>
                      <th className="text-left py-3 px-4 font-medium">หมวด</th>
                      <th className="text-left py-3 px-4 font-medium">ชื่อกฎ</th>
                      <th className="text-right py-3 px-4 font-medium">น้ำหนัก</th>
                      <th className="text-center py-3 px-4 font-medium">สถานะ</th>
                      <th className="text-right py-3 px-4 font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {DEMO_RULES.map((r) => (
                      <tr key={r.rule_id} className="border-b hover:bg-muted/30">
                        <td className="py-2.5 px-4 font-mono text-xs">{r.rule_id}</td>
                        <td className="py-2.5 px-4"><Badge className={`text-[10px] ${catColors[r.category] ?? ""}`}>{r.category}</Badge></td>
                        <td className="py-2.5 px-4">{r.name}</td>
                        <td className="py-2.5 px-4 text-right font-medium">{r.weight}</td>
                        <td className="py-2.5 px-4 text-center">
                          <Badge className={r.active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}>
                            {r.active ? "Active" : "Inactive"}
                          </Badge>
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <Button variant="ghost" size="sm" className="text-xs">แก้ไข</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="templates" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              {DEMO_TEMPLATES.map((t) => (
                <Card key={t.template_id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Badge className="bg-primary/10 text-primary">{t.disease_group}</Badge>
                      <span className="text-xs text-muted-foreground">v{t.version}</span>
                    </div>
                    <CardTitle className="text-base mt-2">{t.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{t.orders_count} รายการสั่งการรักษา</p>
                    <p className="text-xs font-mono text-muted-foreground mt-1">{t.template_id}</p>
                    <Button variant="outline" size="sm" className="mt-3 w-full">ดูรายละเอียด</Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">⚙️ System Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg border p-4">
                    <h3 className="font-medium text-sm">🤖 AI Engine</h3>
                    <p className="text-xs text-muted-foreground mt-1">GraphRAG Knowledge Graph + Rule Engine</p>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="h-2 w-2 rounded-full bg-green-500" />
                      <span className="text-xs text-green-600">Online</span>
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-medium text-sm">🗄️ Database</h3>
                    <p className="text-xs text-muted-foreground mt-1">PostgreSQL 16 + Neo4j 5 + Redis 7</p>
                    <div className="flex items-center gap-2 mt-2">
                      <div className="h-2 w-2 rounded-full bg-green-500" />
                      <span className="text-xs text-green-600">Connected</span>
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-medium text-sm">💰 RW Base Rate</h3>
                    <p className="text-xs text-muted-foreground mt-1">฿12,000 / RW unit</p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-medium text-sm">📊 Disease Groups</h3>
                    <p className="text-xs text-muted-foreground mt-1">CAP, DM Complications, Heart Failure</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
