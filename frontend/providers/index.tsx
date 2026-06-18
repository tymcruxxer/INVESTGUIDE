/**
 * Global Providers
 * Combines all application providers
 */

import React from "react";
import { ReactQueryProvider } from "./react-query";
import { ThemeProvider } from "./theme-provider";

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider>
      <ReactQueryProvider>
        {children}
      </ReactQueryProvider>
    </ThemeProvider>
  );
}
