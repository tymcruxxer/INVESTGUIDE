/**
 * Zustand Store Hooks
 * Central state management for authentication, theme, and UI state
 */

import { create } from "zustand";
import {
  AuthState,
  AuthTokens,
  ExperienceLevel,
  InvestorProfile,
  InvestorProfilePayload,
  RiskProfile,
  User,
} from "@/types";
import {
  authService,
  getStoredAccessToken,
  handleApiError,
  investorProfileService,
  setStoredAccessToken,
} from "@/services/api";

// ============================================================================
// Auth Store
// ============================================================================

interface AuthStoreState extends AuthState {
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setInvestorProfile: (profile: InvestorProfile | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  hydrateSession: () => Promise<void>;
  refreshProfile: () => Promise<InvestorProfile | null>;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  completeOnboarding: (payload: InvestorProfilePayload) => Promise<void>;
  updateUserProfile: (
    riskProfile: RiskProfile,
    experienceLevel: ExperienceLevel
  ) => Promise<void>;
}

const tokenToAuthTokens = (token: string): AuthTokens => ({
  access_token: token,
  token_type: "bearer",
});

export const useAuthStore = create<AuthStoreState>((set, getState) => ({
  isAuthenticated: false,
  user: null,
  tokens: null,
  investorProfile: null,
  onboardingComplete: false,
  hydrated: false,
  loading: false,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: user !== null }),
  setTokens: (tokens) => set({ tokens }),
  setInvestorProfile: (profile) =>
    set({ investorProfile: profile, onboardingComplete: profile !== null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  hydrateSession: async () => {
    const token = getStoredAccessToken();
    if (!token) {
      set({
        hydrated: true,
        isAuthenticated: false,
        user: null,
        tokens: null,
        investorProfile: null,
        onboardingComplete: false,
      });
      return;
    }

    set({ loading: true, error: null, tokens: tokenToAuthTokens(token) });
    try {
      const userResponse = await authService.me();
      set({ user: userResponse.data, isAuthenticated: true });
      await getState().refreshProfile();
    } catch (error) {
      setStoredAccessToken(null);
      set({
        user: null,
        tokens: null,
        investorProfile: null,
        isAuthenticated: false,
        onboardingComplete: false,
        error: handleApiError(error),
      });
    } finally {
      set({ hydrated: true, loading: false });
    }
  },

  refreshProfile: async () => {
    try {
      const profileResponse = await investorProfileService.getProfile();
      set({
        investorProfile: profileResponse.data,
        onboardingComplete: profileResponse.data !== null,
      });
      return profileResponse.data;
    } catch {
      set({ investorProfile: null, onboardingComplete: false });
      return null;
    }
  },

  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const response = await authService.login(email, password);
      set({
        user: response.data.user,
        tokens: {
          access_token: response.data.access_token,
          token_type: response.data.token_type,
        },
        isAuthenticated: true,
      });
      await getState().refreshProfile();
    } catch (error) {
      const message = handleApiError(error);
      set({ error: message });
      throw new Error(message);
    } finally {
      set({ loading: false, hydrated: true });
    }
  },

  signup: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const response = await authService.signup(email, password);
      set({
        user: response.data.user,
        tokens: {
          access_token: response.data.access_token,
          token_type: response.data.token_type,
        },
        investorProfile: null,
        isAuthenticated: true,
        onboardingComplete: false,
      });
    } catch (error) {
      const message = handleApiError(error);
      set({ error: message });
      throw new Error(message);
    } finally {
      set({ loading: false, hydrated: true });
    }
  },

  logout: () => {
    authService.logout();
    set({
      user: null,
      tokens: null,
      investorProfile: null,
      isAuthenticated: false,
      onboardingComplete: false,
      error: null,
      hydrated: true,
    });
  },

  completeOnboarding: async (payload: InvestorProfilePayload) => {
    set({ loading: true, error: null });
    try {
      const existingProfile = getState().investorProfile;
      const response = existingProfile
        ? await investorProfileService.updateProfile(payload)
        : await investorProfileService.createProfile(payload);
      set({ investorProfile: response.data, onboardingComplete: true });
    } catch (error) {
      const message = handleApiError(error);
      set({ error: message });
      throw new Error(message);
    } finally {
      set({ loading: false });
    }
  },

  updateUserProfile: async (riskProfile, experienceLevel) => {
    await getState().completeOnboarding({
      risk_appetite: riskProfile,
      experience_level: experienceLevel,
    });
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
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  mobileMenuOpen: false,
  setMobileMenuOpen: (open) => set({ mobileMenuOpen: open }),
}));
