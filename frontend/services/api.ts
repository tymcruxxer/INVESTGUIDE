/**
 * API Service Layer
 * Centralized API client for all backend communication
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import { ApiResponse, ApiError } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Create and configure axios instance
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config) => {
      if (typeof window !== "undefined") {
        const token = localStorage.getItem("access_token");
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => {
      if (error.response?.status === 401) {
        // Handle unauthorized - redirect to login
        if (typeof window !== "undefined") {
          localStorage.removeItem("access_token");
          window.location.href = "/auth/login";
        }
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

/**
 * Generic GET request
 */
export async function get<T>(
  url: string,
  params?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.get<ApiResponse<T>>(url, { params });
  return response.data;
}

/**
 * Generic POST request
 */
export async function post<T>(
  url: string,
  data?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.post<ApiResponse<T>>(url, data);
  return response.data;
}

/**
 * Generic PATCH request
 */
export async function patch<T>(
  url: string,
  data?: Record<string, unknown>
): Promise<ApiResponse<T>> {
  const response = await apiClient.patch<ApiResponse<T>>(url, data);
  return response.data;
}

/**
 * Generic DELETE request
 */
export async function delete_<T>(url: string): Promise<ApiResponse<T>> {
  const response = await apiClient.delete<ApiResponse<T>>(url);
  return response.data;
}

// ============================================================================
// Asset Services
// ============================================================================

export const assetService = {
  /**
   * Get all assets with filters
   */
  getAssets: (params: {
    page?: number;
    limit?: number;
    search?: string;
    exchange?: string;
    sector?: string;
  }) => get("/assets", params),

  /**
   * Get asset by ticker
   */
  getAssetByTicker: (ticker: string) => get(`/assets/${ticker}`),

  /**
   * Get historical prices
   */
  getHistoricalPrices: (ticker: string, params?: { days?: number }) =>
    get(`/assets/${ticker}/prices`, params),

  /**
   * Get sentiment analysis
   */
  getSentiment: (ticker: string) => get(`/assets/${ticker}/sentiment`),

  /**
   * Get analytics metrics
   */
  getAnalytics: (ticker: string) => get(`/assets/${ticker}/analytics`),

  /**
   * Get AI summary
   */
  getAiSummary: (ticker: string) => get(`/assets/${ticker}/ai-summary`),

  /**
   * Get asset news
   */
  getAssetNews: (ticker: string, params?: { limit?: number }) =>
    get(`/assets/${ticker}/news`, params),
};

// ============================================================================
// News Services
// ============================================================================

export const newsService = {
  /**
   * Get news feed
   */
  getNewsFeed: (params: { page?: number; limit?: number; category?: string }) =>
    get("/news", params),

  /**
   * Get news by asset
   */
  getNewsByAsset: (ticker: string) => get(`/assets/${ticker}/news`),
};

// ============================================================================
// Macro Services
// ============================================================================

export const macroService = {
  /**
   * Get macro overview
   */
  getOverview: () => get("/macro/overview"),

  /**
   * Get inflation data
   */
  getInflation: () => get("/macro/inflation"),

  /**
   * Get exchange rate
   */
  getExchangeRate: () => get("/macro/exchange-rate"),
};

// ============================================================================
// Watchlist Services
// ============================================================================

export const watchlistService = {
  /**
   * Get user watchlist
   */
  getWatchlist: () => get("/watchlists"),

  /**
   * Add to watchlist
   */
  addToWatchlist: (assetId: number) =>
    post("/watchlists", { asset_id: assetId }),

  /**
   * Remove from watchlist
   */
  removeFromWatchlist: (watchlistId: number) =>
    delete_(`/watchlists/${watchlistId}`),
};

// ============================================================================
// AI Chat Services
// ============================================================================

export const aiService = {
  /**
   * Send message to AI assistant
   */
  chat: (message: string) =>
    post("/ai/chat", { message }),
};

/**
 * Handle API errors
 */
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
