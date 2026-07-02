/**
 * Auth Session Provider
 * Hydrates persisted client-side auth state on application load.
 */

"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store";

interface AuthSessionProviderProps {
  children: React.ReactNode;
}

export function AuthSessionProvider({ children }: AuthSessionProviderProps) {
  const hydrateSession = useAuthStore((state) => state.hydrateSession);

  useEffect(() => {
    void hydrateSession();
  }, [hydrateSession]);

  return <>{children}</>;
}
