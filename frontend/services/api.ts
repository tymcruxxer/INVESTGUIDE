/**
 * API Service Layer
 * Centralized API client for all backend communication
 */

import axios, { AxiosError, AxiosInstance } from "axios";
import {
  ApiError,
  ApiResponse,
  Asset,
  AssetAssessment,
  AuthResponse,
  Company,
  CompanyDetail,
  InvestorProfile,
  InvestorProfilePayload,
  NewsArticle,
  SignupResponse,
  User,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const ACCESS_TOKEN_KEY = "investguide_access_token";

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setStoredAccessToken(token: string | null): void {
  if (typeof window === "undefined") {
    return;
  }
  if (token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
    localStorage.setItem("access_token", token);
    return;
  }
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem("access_token");
}

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  client.interceptors.request.use(
    (config) => {
      const token = getStoredAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => {
      if (error.response?.status === 401 && typeof window !== "undefined") {
        setStoredAccessToken(null);
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

export async function get<T>(
  url: string,
  params?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data;
}

export async function post<T>(
  url: string,
  data?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.post<ApiResponse<T>>(url, data);
  return response.data;
}

export async function put<T>(
  url: string,
  data?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.put<ApiResponse<T>>(url, data);
  return response.data;
}

export async function patch<T>(
  url: string,
  data?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.patch<ApiResponse<T>>(url, data);
  return response.data;
}

export async function delete_<T>(url: string): Promise<ApiResponse<T>> {
  const response = await apiClient.delete<ApiResponse<T>>(url);
  return response.data;
}

// ============================================================================
// Auth Services
// ============================================================================

export const authService = {
  login: async (email: string, password: string) => {
    const response = await post<AuthResponse>("/auth/login", { email, password });
    setStoredAccessToken(response.data.access_token);
    return response;
  },

  signup: async (email: string, password: string) => {
    const response = await post<SignupResponse>("/auth/signup", {
      email,
      password,
    });
    setStoredAccessToken(response.data.access_token);
    return response;
  },

  me: () => get<User>("/auth/me"),

  logout: () => setStoredAccessToken(null),
};

// ============================================================================
// Investor Profile Services
// ============================================================================

export const investorProfileService = {
  getProfile: () => get<InvestorProfile>("/investor-profile"),

  createProfile: (payload: InvestorProfilePayload) =>
    post<InvestorProfile>("/investor-profile", payload as Record<string, unknown>),

  updateProfile: (payload: InvestorProfilePayload) =>
    put<InvestorProfile>("/investor-profile", payload as Record<string, unknown>),
};

// ============================================================================
// Asset Services
// ============================================================================

export const assetService = {
  getAssets: (params: {
    page?: number;
    limit?: number;
    search?: string;
    exchange?: string;
    sector?: string;
    asset_type?: string;
    status?: string;
  } = {}) => get<Asset[]>("/assets", params),

  getAssetByTicker: (ticker: string) => get<Asset>(`/assets/${ticker}`),

  getAssetAssessment: (ticker: string) => get<AssetAssessment>(`/assets/${ticker}/assessment`),

  getHistoricalPrices: (ticker: string, params?: { days?: number }) =>
    get(`/assets/${ticker}/prices`, params),

  getSentiment: (ticker: string) => get(`/assets/${ticker}/sentiment`),

  getAnalytics: (ticker: string) => get(`/assets/${ticker}/analytics`),

  getAiSummary: (ticker: string) => get(`/assets/${ticker}/ai-summary`),

  getAssetNews: (ticker: string, params?: { limit?: number }) =>
    get<NewsArticle[]>("/news", { ...(params ?? {}), asset: ticker }),
};
// ============================================================================
// News Services
// ============================================================================

export const newsService = {
  getNewsFeed: (params: {
    page?: number;
    limit?: number;
    source?: string;
    asset?: string;
    search?: string;
    sort?: "asc" | "desc";
  } = {}) => get<NewsArticle[]>("/news", params),

  getNewsById: (id: number) => get<NewsArticle>(`/news/${id}`),

  getNewsByAsset: (ticker: string, params?: { limit?: number }) =>
    get<NewsArticle[]>("/news", { ...(params ?? {}), asset: ticker }),
};

export const companyService = {
  getCompanies: (params: {
    page?: number;
    limit?: number;
    search?: string;
    exchange?: string;
    sector?: string;
    industry?: string;
  } = {}) => get<Company[]>("/companies", params),

  getCompanyByTicker: (ticker: string) => get<CompanyDetail>(`/companies/${ticker}`),

  getCompanyAssessment: (ticker: string) => get<AssetAssessment>(`/companies/${ticker}/assessment`),
};

// ============================================================================
// Macro Services
// ============================================================================

export const macroService = {
  getOverview: () => get("/macro/overview"),

  getInflation: () => get("/macro/inflation"),

  getExchangeRate: () => get("/macro/exchange-rate"),
};

// ============================================================================
// Watchlist Services
// ============================================================================

export const watchlistService = {
  getWatchlist: () => get("/watchlists"),

  addToWatchlist: (assetId: number) => post("/watchlists", { asset_id: assetId }),

  removeFromWatchlist: (watchlistId: number) => delete_(`/watchlists/${watchlistId}`),
};

// ============================================================================
// AI Chat Services
// ============================================================================

export const aiService = {
  chat: (message: string) => post("/ai/chat", { message }),
};

export function handleApiError(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response?.data) {
      const apiError = error.response.data as ApiError;
      return apiError.message || "An error occurred";
    }
    return error.message || "Network error";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unknown error occurred";
}
