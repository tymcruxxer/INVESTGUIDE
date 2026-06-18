/**
 * Zustand Store Hooks
 * Central state management for authentication, theme, and UI state
 */

import { create } from "zustand";
import { AuthState, User, AuthTokens, RiskProfile, ExperienceLevel } from "@/types";

// ============================================================================
// Auth Store
// ============================================================================

interface AuthStoreState extends AuthState {
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<void>;
  logout: () => void;
  updateUserProfile: (
    riskProfile: RiskProfile,
    experienceLevel: ExperienceLevel
  ) => Promise<void>;
}

export const useAuthStore = create<AuthStoreState>((set) => ({
  isAuthenticated: false,
  user: null,
  tokens: null,
  loading: false,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: user !== null }),
  setTokens: (tokens) => set({ tokens }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  login: async (_email: string, _password: string) => {
    set({ loading: true, error: null });
    try {
      // TODO: API call to /api/v1/auth/login
      // const response = await authService.login(email, password);
      // set({
      //   user: response.data.user,
      //   tokens: response.data.tokens,
      //   isAuthenticated: true,
      // });
      set({ loading: false });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Login failed";
      set({ error: message, loading: false });
      throw error;
    }
  },

  register: async (
    _email: string,
    _password: string,
    _fullName: string
  ) => {
    set({ loading: true, error: null });
    try {
      // TODO: API call to /api/v1/auth/register
      // const response = await authService.register(email, password, fullName);
      // set({
      //   user: response.data.user,
      //   tokens: response.data.tokens,
      //   isAuthenticated: true,
      // });
      set({ loading: false });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Registration failed";
      set({ error: message, loading: false });
      throw error;
    }
  },

  logout: () => {
    set({
      user: null,
      tokens: null,
      isAuthenticated: false,
      error: null,
    });
    // TODO: Clear localStorage tokens
  },

  updateUserProfile: async (
    _riskProfile: RiskProfile,
    _experienceLevel: ExperienceLevel
  ) => {
    set({ loading: true, error: null });
    try {
      // TODO: API call to /api/v1/users/preferences
      // const response = await userService.updatePreferences(riskProfile, experienceLevel);
      // set({ user: response.data });
      set({ loading: false });
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Update profile failed";
      set({ error: message, loading: false });
      throw error;
    }
  },
}));

// ============================================================================
// Theme Store
// ============================================================================

type Theme = "dark" | "light" | "system";

interface ThemeStoreState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeStoreState>((set) => ({
  theme: "dark",

  setTheme: (theme) => {
    set({ theme });
    if (typeof document !== "undefined") {
      const root = document.documentElement;
      if (theme === "dark") {
        root.classList.remove("light");
        localStorage.setItem("theme", "dark");
      } else if (theme === "light") {
        root.classList.add("light");
        localStorage.setItem("theme", "light");
      } else {
        root.classList.toggle("light");
        localStorage.removeItem("theme");
      }
    }
  },

  toggleTheme: () =>
    set((state) => {
      const newTheme = state.theme === "dark" ? "light" : "dark";
      if (typeof document !== "undefined") {
        const root = document.documentElement;
        if (newTheme === "dark") {
          root.classList.remove("light");
        } else {
          root.classList.add("light");
        }
      }
      return { theme: newTheme };
    }),
}));

// ============================================================================
// UI Store
// ============================================================================

interface UIStoreState {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStoreState>((set) => ({
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  mobileMenuOpen: false,
  setMobileMenuOpen: (open) => set({ mobileMenuOpen: open }),
}));
