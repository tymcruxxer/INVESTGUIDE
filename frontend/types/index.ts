/**
 * Type Definitions for InvestGuide Frontend
 * Shared TypeScript types used across the application
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    has_next?: boolean;
  };
}

export interface ApiError {
  success: false;
  message: string;
  error_code: string;
  details?: Record<string, unknown>;
}

// ============================================================================
// Asset Types
// ============================================================================

export type Exchange = "ZSE" | "VFEX";
export type AssetType = "equity" | "REIT" | "bond";
export type Currency = "ZWG" | "USD";
export type SentimentLabel = "positive" | "neutral" | "negative";
export type RiskLevel = "low" | "moderate" | "high" | "speculative";

export interface Asset {
  id: number;
  ticker: string;
  company_name: string;
  exchange: Exchange;
  sector: string;
  industry: string;
  asset_type: AssetType;
  currency: Currency;
  description: string;
  logo_url?: string;
  official_website?: string;
  market_cap?: number;
  listing_date?: string;
  status: "active" | "suspended";
  created_at: string;
}

export interface HistoricalPrice {
  id: number;
  asset_id: number;
  date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  adjusted_close: number;
  volume: number;
  currency: Currency;
  created_at: string;
}

export interface AssetDetail extends Asset {
  current_price?: number;
  price_change?: number;
  price_change_percent?: number;
  sentiment?: SentimentAnalysis;
  analytics?: AnalyticsMetrics;
  dividend_yield?: number;
}

// ============================================================================
// Sentiment Types
// ============================================================================

export interface SentimentAnalysis {
  sentiment_score: number; // -1.0 to 1.0
  sentiment_label: SentimentLabel;
  confidence_score: number; // 0.0 to 1.0
  model_used: string;
  processed_at: string;
}

export interface MarketSentiment {
  positive_count: number;
  neutral_count: number;
  negative_count: number;
  aggregate_score: number;
  institutional_outlook: string;
  market_momentum: string;
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface AnalyticsMetrics {
  performance_score: number; // 0-100
  risk_score: number; // 0-100
  momentum_score: number; // 0-100
  dividend_stability: number; // 0-100
  volatility: number; // percentage
  risk_level: RiskLevel;
  liquidity_score: number; // 0-100
}

export interface RecommendationScore {
  final_score: number; // 0-100
  recommendation: "strong" | "moderate" | "caution";
  performance_weight: number;
  risk_weight: number;
  sentiment_weight: number;
  macro_weight: number;
  dividend_weight: number;
  reasoning: string;
}

// ============================================================================
// News & Research Types
// ============================================================================

export interface NewsArticle {
  id: number;
  source_name: string;
  source_url: string;
  article_title: string;
  article_content: string;
  summary?: string;
  publication_date: string;
  author?: string;
  category: "markets" | "macro" | "company" | "research";
  sentiment_status: "pending" | "processed";
  created_at: string;
}

export interface AiSummary {
  id: number;
  asset_id?: number;
  summary_type: "company" | "market" | "sector" | "macro";
  summary_content: string;
  model_used: string;
  generated_at: string;
  expiration_time: string;
}

// ============================================================================
// Macroeconomic Types
// ============================================================================

export interface MacroIndicator {
  id: number;
  indicator_name: string; // inflation, exchange_rate, interest_rate, gold_price
  indicator_value: number;
  indicator_unit: string;
  source: "RBZ" | "ZIMSTAT";
  reporting_date: string;
  category: "monetary" | "fiscal" | "commodity";
  created_at: string;
}

export interface MacroOverview {
  inflation_rate?: number;
  exchange_rate?: number;
  interest_rate?: number;
  gold_price?: number;
  unemployment_rate?: number;
  gdp_growth?: number;
  last_updated: string;
}

// ============================================================================
// User & Authentication Types
// ============================================================================

export type UserRole = "user" | "admin" | "moderator";
export type RiskProfile = "conservative" | "moderate" | "aggressive";
export type ExperienceLevel = "beginner" | "intermediate" | "advanced";

export interface User {
  id: number;
  full_name: string;
  email: string;
  subscription_plan: "free" | "premium";
  risk_profile: RiskProfile;
  experience_level: ExperienceLevel;
  preferred_investments?: string[];
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  tokens: AuthTokens | null;
  loading: boolean;
  error: string | null;
}

// ============================================================================
// Watchlist & Alert Types
// ============================================================================

export interface Watchlist {
  id: number;
  user_id: number;
  asset_id: number;
  asset?: Asset;
  created_at: string;
}

export type AlertType = "price_change" | "sentiment" | "dividend" | "macro";

export interface Alert {
  id: number;
  user_id: number;
  asset_id: number;
  alert_type: AlertType;
  threshold: number;
  is_active: boolean;
  triggered_at?: string;
  created_at: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface LoadingState {
  isLoading: boolean;
  error: Error | null;
  isError: boolean;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface FilterOptions {
  search?: string;
  sector?: string;
  exchange?: Exchange;
  asset_type?: AssetType;
  risk_level?: RiskLevel;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  limit?: number;
}

// ============================================================================
// Feature-Specific Types
// ============================================================================

export interface DashboardWidget {
  id: string;
  title: string;
  type: string;
  config: Record<string, unknown>;
  order: number;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  sentiment?: number;
}
