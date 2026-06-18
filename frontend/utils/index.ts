/**
 * Utility Functions
 * Shared helper functions used across the application
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combine Tailwind classes safely using clsx and twMerge
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency value with appropriate symbol
 */
export function formatCurrency(
  value: number | undefined,
  currency: "ZWG" | "USD" = "ZWG"
): string {
  if (value === undefined || value === null) return "-";
  const symbol = currency === "USD" ? "$" : "ZWG";
  return `${symbol} ${value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/**
 * Format percentage with sign
 */
export function formatPercent(
  value: number | undefined,
  decimals = 2
): string {
  if (value === undefined || value === null) return "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format large numbers with suffixes (K, M, B)
 */
export function formatLargeNumber(value: number | undefined): string {
  if (value === undefined || value === null) return "-";

  const abs = Math.abs(value);
  if (abs >= 1e9) {
    return (value / 1e9).toFixed(1) + "B";
  }
  if (abs >= 1e6) {
    return (value / 1e6).toFixed(1) + "M";
  }
  if (abs >= 1e3) {
    return (value / 1e3).toFixed(1) + "K";
  }
  return value.toFixed(0);
}

/**
 * Format date string to readable format
 */
export function formatDate(
  date: string | Date,
  format: "short" | "long" = "short"
): string {
  const d = typeof date === "string" ? new Date(date) : date;

  if (format === "short") {
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Format time to HH:MM:SS
 */
export function formatTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let previous = 0;

  return function executedFunction(...args: Parameters<T>) {
    const now = Date.now();
    const remaining = wait - (now - previous);

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      func(...args);
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now();
        timeout = null;
        func(...args);
      }, remaining);
    }
  };
}

/**
 * Get sentiment color based on sentiment score
 */
export function getSentimentColor(score: number): string {
  if (score > 0.3) return "text-emerald-500";
  if (score < -0.3) return "text-red-500";
  return "text-gray-500";
}

/**
 * Get sentiment label based on score
 */
export function getSentimentLabel(score: number): string {
  if (score > 0.3) return "Positive";
  if (score < -0.3) return "Negative";
  return "Neutral";
}

/**
 * Get risk level color
 */
export function getRiskLevelColor(level: "low" | "moderate" | "high" | "speculative"): string {
  switch (level) {
    case "low":
      return "text-emerald-500";
    case "moderate":
      return "text-yellow-500";
    case "high":
      return "text-orange-500";
    case "speculative":
      return "text-red-500";
    default:
      return "text-gray-500";
  }
}

/**
 * Get recommendation badge color
 */
export function getRecommendationColor(recommendation: "strong" | "moderate" | "caution"): string {
  switch (recommendation) {
    case "strong":
      return "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
    case "moderate":
      return "bg-blue-500/10 text-blue-500 border-blue-500/20";
    case "caution":
      return "bg-red-500/10 text-red-500 border-red-500/20";
    default:
      return "bg-gray-500/10 text-gray-500 border-gray-500/20";
  }
}

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
}

/**
 * Check if date is today
 */
export function isToday(date: Date): boolean {
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

/**
 * Calculate days between two dates
 */
export function daysBetween(date1: Date, date2: Date): number {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  const diffTime = Math.abs(d2.getTime() - d1.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}
