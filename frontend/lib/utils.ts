import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | null | undefined, currency: string = "₹"): string {
  if (value === null || value === undefined || isNaN(value)) return "N/A";
  if (value >= 1e12) return `${currency}${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `${currency}${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e7) return `${currency}${(value / 1e7).toFixed(2)}Cr`;
  if (value >= 1e5) return `${currency}${(value / 1e5).toFixed(2)}L`;
  return `${currency}${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) return "N/A";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}
