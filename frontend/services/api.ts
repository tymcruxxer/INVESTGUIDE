/**
 * API Service Layer
 * Centralized API client for all backend communication
 */

import axios, { AxiosError, AxiosInstance } from "axios";
import {
  ApiError,
  AdminMe,
  AdminNavigationPayload,
  AdminPermissionsPayload,
  AdminRole,
  AdminRoleMutationPayload,
  AdminUserDetail,
  AdminUserListPayload,
  AdminUserStatusPayload,
  ApiResponse,
  Asset,
  AssetAssessment,
  AuthResponse,
  BusinessIntelligence,
  Company,
  CompanyDataQualityPayload,
  CompanyDetail,
  CompanyDividendIntelligencePayload,
  CompanyDividendsPayload,
  CompanyFinancialHealthPayload,
  CompanyFinancialStatementIntelligencePayload,
  CompanyFinancialStatementsPayload,
  CompanyFinancialsPayload,
  CompanyProfileDetail,
  CompanyRelatedResearch,
  ComparePayload,
  DataQualitySummaryPayload,
  EntityQualityPayload,
  CompanyMacroImpactPayload,
  MacroIndicatorPayload,
  MacroOverviewPayload,
  MacroResearchPayload,
  IngestionRecordIssue,
  IngestionRunDetailPayload,
  IngestionRunSummary,
  InvestorProfile,
  InvestorProfilePayload,
  NewsArticle,
  NewsResearch,
  ResearchAssessment,
  SignupResponse,
  SourceHealthPayload,
  SectorDetailPayload,
  SectorRecord,
  SectorResearchPayload,
  IndustryRecord,
  IndustryResearchPayload,
  User,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001/api/v1";
const ACCESS_TOKEN_KEY = "investguide_access_token";
const LOCAL_BACKEND_URL = "http://127.0.0.1:8001";
const BACKEND_UNREACHABLE_MESSAGE =
  "Backend is not reachable. Please make sure the backend is running on http://127.0.0.1:8001.";

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

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export function getBackendHealthUrl(): string {
  try {
    return new URL(API_BASE_URL).origin;
  } catch {
    return LOCAL_BACKEND_URL;
  }
}

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
// Admin Services
// ============================================================================

export const adminService = {
  me: () => get<AdminMe>("/admin/me"),
  navigation: () => get<AdminNavigationPayload>("/admin/navigation"),
  permissions: () => get<AdminPermissionsPayload>("/admin/permissions"),
  users: (params: Record<string, unknown> = {}) => get<AdminUserListPayload>("/admin/users", params),
  user: (id: number) => get<AdminUserDetail>(`/admin/users/${id}`),
  updateUserRoles: (id: number, payload: AdminRoleMutationPayload) =>
    patch<AdminUserDetail>(`/admin/users/${id}/roles`, payload as unknown as Record<string, unknown>),
  updateUserStatus: (id: number, payload: AdminUserStatusPayload) =>
    patch<AdminUserDetail>(`/admin/users/${id}/status`, payload as unknown as Record<string, unknown>),
  roles: () => get<AdminRole[]>("/admin/roles"),
  role: (id: number) => get<AdminRole>(`/admin/roles/${id}`),
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

  getAssetResearch: (ticker: string) => get<ResearchAssessment>(`/assets/${ticker}/research`),

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

  getNewsResearch: (id: number) => get<NewsResearch>(`/news/${id}/research`),

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

  getCompanyBusiness: (ticker: string) => get<BusinessIntelligence>(`/companies/${ticker}/business`),

  getCompanyFinancials: (ticker: string) => get<CompanyFinancialsPayload>(`/companies/${ticker}/financials`),

  getCompanyFinancialStatements: (ticker: string) => get<CompanyFinancialStatementsPayload>(`/companies/${ticker}/financial-statements`),

  getCompanyFinancialStatementIntelligence: (ticker: string) => get<CompanyFinancialStatementIntelligencePayload>(`/companies/${ticker}/financial-intelligence`),
  getCompanyDividends: (ticker: string) => get<CompanyDividendsPayload>(`/companies/${ticker}/dividends`),

  getCompanyDividendIntelligence: (ticker: string) => get<CompanyDividendIntelligencePayload>(`/companies/${ticker}/dividend-intelligence`),

  getCompanyFinancialHealth: (ticker: string) => get<CompanyFinancialHealthPayload>(`/companies/${ticker}/financial-health`),

  getCompanyResearch: (ticker: string) => get<ResearchAssessment>(`/companies/${ticker}/research`),

  getCompanyProfile: (ticker: string) => get<CompanyProfileDetail>(`/companies/${ticker}/profile`),

  getCompanyRelated: (ticker: string) => get<CompanyRelatedResearch>(`/companies/${ticker}/related`),
};

export const comparisonService = {
  compareAssets: (assetA: string, assetB: string) =>
    get<ComparePayload>("/compare", { asset_a: assetA, asset_b: assetB }),

  compareCompanies: (companyA: string, companyB: string) =>
    get<ComparePayload>("/compare", { company_a: companyA, company_b: companyB }),
};

export const sectorService = {
  getSectors: () => get<SectorRecord[]>("/sectors"),

  getSector: (slug: string) => get<SectorDetailPayload>(`/sectors/${encodeURIComponent(slug)}`),

  getSectorResearch: (slug: string) => get<SectorResearchPayload>(`/sectors/${encodeURIComponent(slug)}/research`),
};

export const industryService = {
  getIndustries: () => get<IndustryRecord[]>("/industries"),

  getIndustry: (industry: string) =>
    get<IndustryRecord>(`/industries/${encodeURIComponent(industry)}`),

  getIndustryResearch: (industry: string) =>
    get<IndustryResearchPayload>(`/industries/${encodeURIComponent(industry)}/research`),
};
// ============================================================================
// Macro Services
// ============================================================================

export const macroService = {
  getOverview: () => get<MacroOverviewPayload>("/macro"),

  getIndicator: (type: string) => get<MacroIndicatorPayload>(`/macro/${type}`),

  getResearch: (type: string) => get<MacroResearchPayload>(`/macro/${type}/research`),

  getCompanyImpact: (ticker: string) => get<CompanyMacroImpactPayload>(`/macro/company/${ticker}`),
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
  if (axios.isAxiosError<ApiError>(error)) {
    if (!error.response) {
      return BACKEND_UNREACHABLE_MESSAGE;
    }
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











export const internalOperationsService = {
  getRuns: (params: { page?: number; limit?: number } = {}) =>
    get<IngestionRunSummary[]>("/internal/ingestion/runs", params),

  getRunDetail: (runId: number) =>
    get<IngestionRunDetailPayload>(`/internal/ingestion/runs/${runId}`),

  getRunIssues: (runId: number, params: { page?: number; limit?: number; severity?: string; issue_code?: string } = {}) =>
    get<IngestionRecordIssue[]>(`/internal/ingestion/runs/${runId}/issues`, params),

  getSources: () => get<SourceHealthPayload[]>("/internal/ingestion/sources"),

  getDataQualitySummary: () => get<DataQualitySummaryPayload>("/internal/data-quality/summary"),

  getEntityQuality: (entityType: string) =>
    get<EntityQualityPayload>(`/internal/data-quality/entities/${entityType}`),

  getCompanyQuality: (ticker: string) =>
    get<CompanyDataQualityPayload>(`/internal/data-quality/companies/${ticker}`),
};










