import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function formatThaiDate(dateStr: string): string {
  const d = new Date(dateStr);
  const thaiMonths = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."];
  return `${d.getDate()} ${thaiMonths[d.getMonth()]} ${d.getFullYear() + 543}`;
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("th-TH", { style: "currency", currency: "THB" }).format(amount);
}

export function getScoreColor(score: number): string {
  if (score >= 90) return "text-green-600";
  if (score >= 75) return "text-blue-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

export function getSeverityColor(level: string): string {
  switch (level.toUpperCase()) {
    case "CRITICAL": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    case "HIGH": return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
    case "MODERATE": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    case "LOW": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
  }
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case "ESSENTIAL": return "bg-red-100 text-red-700 border-red-200";
    case "RECOMMENDED": return "bg-blue-100 text-blue-700 border-blue-200";
    case "OPTIONAL": return "bg-gray-100 text-gray-700 border-gray-200";
    default: return "bg-gray-100 text-gray-700 border-gray-200";
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "ACTIVE": return "bg-green-100 text-green-700";
    case "DISCHARGED": return "bg-blue-100 text-blue-700";
    case "PENDING": return "bg-yellow-100 text-yellow-700";
    case "ACCEPTED": return "bg-green-100 text-green-700";
    case "REJECTED": return "bg-red-100 text-red-700";
    default: return "bg-gray-100 text-gray-700";
  }
}
