"use client";

import React from "react";
import AppShell from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn, formatCurrency, getScoreColor } from "@/lib/utils";

const WEEKLY_DATA = [
  { week: "สัปดาห์ 1", avg_score: 62, total_rw: 18.5, revenue_delta: 45000, encounters: 12 },
  { week: "สัปดาห์ 2", avg_score: 68, total_rw: 22.3, revenue_delta: 62000, encounters: 15 },
  { week: "สัปดาห์ 3", avg_score: 71, total_rw: 25.1, revenue_delta: 78000, encounters: 14 },
  { week: "สัปดาห์ 4", avg_score: 75, total_rw: 28.7, revenue_delta: 95000, encounters: 16 },
];

const DISEASE_STATS = [
  { group: "CAP", count: 24, avg_score: 72, avg_rw_delta: 1.85, icon: "🫁" },
  { group: "DM Complications", count: 18, avg_score: 68, avg_rw_delta: 1.42, icon: "💉" },
  { group: "Heart Failure", count: 15, avg_score: 75, avg_rw_delta: 2.15, icon: "❤️" },
];

const TOP_MISSING_CODES = [
  { code: "N17.9", description: "AKI", count: 8, avg_rw: 1.23 },
  { code: "E87.6", description: "Hypokalemia", count: 7, avg_rw: 0.55 },
  { code: "A41.9", description: "Sepsis", count: 5, avg_rw: 2.15 },
  { code: "D64.9", description: "Anemia", count: 5, avg_rw: 0.50 },
  { code: "I10", description: "Hypertension", count: 4, avg_rw: 0.45 },
];

export default function AnalyticsPage() {
  const totalRevenue = WEEKLY_DATA.reduce((a, b) => a + b.revenue_delta, 0);
  const currentAvg = WEEKLY_DATA[WEEKLY_DATA.length - 1].avg_score;
  const prevAvg = WEEKLY_DATA[0].avg_score;
  const improvement = currentAvg - prevAvg;

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">วิเคราะห์ผลลัพธ์</h1>
          <p className="text-muted-foreground">แนวโน้ม RW, Chart Score, และ Revenue Impact</p>
        </div>

        {/* Summary */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Revenue Impact รวม</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(totalRevenue)}</p>
              <p className="text-xs text-muted-foreground mt-1">จากการเพิ่มรหัสที่ขาด</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Chart Score เฉลี่ย</p>
              <p className={cn("text-2xl font-bold", getScoreColor(currentAvg))}>{currentAvg}%</p>
              <p className="text-xs text-green-600 mt-1">↑ {improvement}% จากสัปดาห์แรก</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Encounters ทั้งหมด</p>
              <p className="text-2xl font-bold">{WEEKLY_DATA.reduce((a, b) => a + b.encounters, 0)}</p>
              <p className="text-xs text-muted-foreground mt-1">ใน 4 สัปดาห์</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">RW Delta เฉลี่ย</p>
              <p className="text-2xl font-bold text-primary">+1.81</p>
              <p className="text-xs text-muted-foreground mt-1">ต่อ encounter</p>
            </CardContent>
          </Card>
        </div>

        {/* Weekly Trend (simplified bar chart) */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">📈 แนวโน้มรายสัปดาห์</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              {WEEKLY_DATA.map((w) => (
                <div key={w.week} className="rounded-lg border p-4 text-center space-y-2">
                  <p className="text-sm font-medium">{w.week}</p>
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span>Chart Score</span>
                      <span className={cn("font-bold", getScoreColor(w.avg_score))}>{w.avg_score}%</span>
                    </div>
                    <Progress value={w.avg_score} className="h-2" indicatorClassName={w.avg_score >= 75 ? "bg-green-500" : w.avg_score >= 60 ? "bg-yellow-500" : "bg-red-500"} />
                  </div>
                  <div className="text-xs">
                    <p>RW: {w.total_rw.toFixed(1)}</p>
                    <p className="text-green-600 font-medium">{formatCurrency(w.revenue_delta)}</p>
                    <p className="text-muted-foreground">{w.encounters} cases</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 lg:grid-cols-2">
          {/* Disease Group Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">🏥 สถิติตามกลุ่มโรค</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {DISEASE_STATS.map((d) => (
                <div key={d.group} className="flex items-center gap-4 rounded-lg border p-3">
                  <span className="text-3xl">{d.icon}</span>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{d.group}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                      <span>{d.count} cases</span>
                      <span>Avg Score: <strong className={getScoreColor(d.avg_score)}>{d.avg_score}%</strong></span>
                      <span>Avg RW Δ: <strong className="text-primary">+{d.avg_rw_delta}</strong></span>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Most Common Missing Codes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">🔍 รหัสที่ขาดบ่อยที่สุด</CardTitle>
            </CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium text-muted-foreground">ICD-10</th>
                    <th className="text-left py-2 font-medium text-muted-foreground">Description</th>
                    <th className="text-right py-2 font-medium text-muted-foreground">ครั้ง</th>
                    <th className="text-right py-2 font-medium text-muted-foreground">Avg RW</th>
                  </tr>
                </thead>
                <tbody>
                  {TOP_MISSING_CODES.map((c) => (
                    <tr key={c.code} className="border-b">
                      <td className="py-2 font-mono text-xs">{c.code}</td>
                      <td className="py-2">{c.description}</td>
                      <td className="py-2 text-right font-bold">{c.count}</td>
                      <td className="py-2 text-right text-primary">+{c.avg_rw.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
