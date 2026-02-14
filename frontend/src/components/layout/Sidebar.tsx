"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "แดชบอร์ด", icon: "📊", description: "Dashboard" },
  { href: "/patients/ENC-2567-0001", label: "ผู้ป่วย", icon: "🏥", description: "Patient View" },
  { href: "/admin", label: "ตั้งค่า", icon: "⚙️", description: "Admin" },
  { href: "/analytics", label: "วิเคราะห์", icon: "📈", description: "Analytics" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card transition-transform">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white font-bold text-lg">
          CS
        </div>
        <div>
          <h1 className="text-lg font-bold text-primary">ChartSense AI</h1>
          <p className="text-[10px] text-muted-foreground">Clinical Decision Support</p>
        </div>
      </div>

      <nav className="space-y-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <span className="text-lg">{item.icon}</span>
              <div>
                <div>{item.label}</div>
                <div className="text-[10px] text-muted-foreground">{item.description}</div>
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4 rounded-lg bg-muted p-3">
        <p className="text-xs font-medium">🤖 AI Engine</p>
        <p className="text-[10px] text-muted-foreground">GraphRAG + Rule Engine</p>
        <div className="mt-1 flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[10px] text-green-600">ออนไลน์</span>
        </div>
      </div>
    </aside>
  );
}
