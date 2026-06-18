/**
 * Theme Provider
 * Manages dark/light mode state and applies theme to DOM
 */

"use client";

import React, { useEffect } from "react";
import { useThemeStore } from "@/store";

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const { setTheme } = useThemeStore();

  useEffect(() => {
    // Check localStorage for saved theme
    const savedTheme = localStorage.getItem("theme") as "dark" | "light" | null;
    
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Default to dark mode
      const root = document.documentElement;
      root.classList.remove("light");
      localStorage.setItem("theme", "dark");
    }
  }, [setTheme]);

  return <>{children}</>;
}
