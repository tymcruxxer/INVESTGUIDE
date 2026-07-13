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
export type AssetType = "equity" | "REIT" | "bond" | "money_market" | "alternative";
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
  status: "active" | "suspended" | "delisted";
  created_at: string;
  updated_at?: string;
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
  updated_at?: string;
}

export interface AssetDetail extends Asset {
  current_price?: number;
  price_change?: number;
  price_change_percent?: number;
  sentiment?: SentimentAnalysis;
  analytics?: AnalyticsMetrics;
  dividend_yield?: number;
}

export interface AssetAssessment {
  ticker: string;
  overall_assessment: string;
  evidence_strength: string;
  investment_horizon: string;
  key_strengths: string[];
  things_to_watch: string[];
  educational_summary: string;
  explain_like_im_18: string;
  generated_at: string;
  assessment_version: string;
}


export interface ResearchScoreSection {
  label: string;
  score: number;
  summary: string;
  reasons: string[];
  supporting_evidence: string[];
}

export interface ResearchRiskSection {
  overall_risk: string;
  risk_level: "Low" | "Moderate" | "Elevated" | "High";
  risk_score: number;
  summary: string;
  reasons: string[];
  things_to_watch: string[];
  supporting_evidence: string[];
}

export interface ResearchEvidenceSection {
  strength: "Strong" | "Moderate" | "Limited" | "Experimental";
  score: number;
  summary: string;
  reasons: string[];
  data_used: string[];
  missing_data: string[];
}

export interface ResearchEducationSection {
  summary: string;
  key_concepts: string[];
  why_it_matters: string;
}

export interface ResearchEli18Section {
  summary: string;
  example: string;
}

export interface ResearchOverallSection {
  label: string;
  summary: string;
  reasons: string[];
}

export interface ResearchTransparency {
  data_used: string[];
  assessment_generated: string;
  evidence_strength: string;
  last_updated?: string | null;
  research_status: string;
}

export interface ResearchAssessment {
  ticker: string;
  subject_type: "asset" | "company";
  overall_assessment: ResearchOverallSection;
  opportunity: ResearchScoreSection;
  risk: ResearchRiskSection;
  evidence: ResearchEvidenceSection;
  education: ResearchEducationSection;
  eli18: ResearchEli18Section;
  suggested_questions: string[];
  transparency: ResearchTransparency;
  generated_at: string;
  assessment_version: string;
  engine_version: string;
}
export interface Company {
  id: number;
  name: string;
  legal_name?: string | null;
  ticker: string;
  exchange: Exchange;
  sector?: string | null;
  industry?: string | null;
  country?: string | null;
  headquarters?: string | null;
  website?: string | null;
  description?: string | null;
  founded_year?: number | null;
  employee_count?: number | null;
  market?: string | null;
  currency?: Currency | null;
  status: "active" | "suspended" | "delisted";
  logo_url?: string | null;
  created_at: string;
  updated_at?: string;
}


export type ResearchStatus = "development" | "verified" | "needs_review" | "unavailable";

export interface CompanyProfile {
  id?: number | null;
  company_id?: number | null;
  business_summary?: string | null;
  primary_business?: string | null;
  products_services: string[];
  industry?: string | null;
  sub_industry?: string | null;
  headquarters?: string | null;
  founded_year?: number | null;
  website?: string | null;
  email?: string | null;
  phone?: string | null;
  country?: string | null;
  exchange?: Exchange | null;
  currency?: Currency | null;
  employees?: number | null;
  status?: "active" | "suspended" | "delisted" | null;
  research_status: ResearchStatus;
  last_verified?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface CompanyProfileVerification {
  last_verified?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  research_status: ResearchStatus;
}

export interface CompanyProfileDetail {
  company: Company;
  profile: CompanyProfile | null;
  verification: CompanyProfileVerification;
}


export interface LearnNextTopic {
  topic: string;
  why_it_matters: string;
  path: string;
}

export interface KnowledgeGraphEdge {
  from: string;
  to: string;
  reason: string;
}

export interface KnowledgeGraphPayload {
  version: string;
  root: string;
  nodes: string[];
  edges: KnowledgeGraphEdge[];
  learn_next: LearnNextTopic[];
}

export interface RelatedCompanyItem {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  exchange: string;
  relationship_score: number;
  reasons: string[];
  href: string;
}

export interface RelatedNamedItem {
  name: string;
  reason: string;
}

export interface CompanyRelatedResearch {
  version: string;
  ticker: string;
  related_companies: RelatedCompanyItem[];
  related_sectors: RelatedNamedItem[];
  related_asset_types: RelatedNamedItem[];
  educational_topics: LearnNextTopic[];
  knowledge_graph: KnowledgeGraphPayload;
  transparency: {
    methodology: string;
    not_recommendation: string;
  };
}

export interface CompareSubjectSummary {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  exchange: string;
  asset_type: string;
  opportunity_label: string;
  risk_level: string;
  evidence_strength: string;
}

export interface CompareBusinessRow {
  label: string;
  left: string;
  right: string;
  insight: string;
}

export interface ComparePayload {
  version: string;
  subject_type: "asset" | "company";
  left: CompareSubjectSummary;
  right: CompareSubjectSummary;
  summary: string;
  business_comparison: {
    summary: string;
    rows: CompareBusinessRow[];
  };
  opportunity_comparison: {
    summary: string;
    left: { label: string; score: number; reasons: string[] };
    right: { label: string; score: number; reasons: string[] };
    differences: string[];
  };
  risk_comparison: {
    summary: string;
    left: { risk_level: string; score: number; drivers: string[] };
    right: { risk_level: string; score: number; drivers: string[] };
    things_to_watch: string[];
  };
  evidence_comparison: {
    summary: string;
    stronger_evidence: "left" | "right" | "similar";
    left: { strength: string; score: number; data_used: string[] };
    right: { strength: string; score: number; data_used: string[] };
    why: string;
  };
  educational_comparison: {
    summary: string;
    plain_english: string[];
  };
  suggested_follow_up_questions: string[];
  knowledge_paths: {
    left: LearnNextTopic[];
    right: LearnNextTopic[];
  };
  transparency: {
    methodology: string;
    not_recommendation: string;
  };
}
export interface BusinessDriver {
  name: string;
  why_it_matters: string;
}

export interface BusinessCompetitorItem {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  relationship_score: number;
  relationship_type: string;
  reasons: string[];
  href: string;
}

export interface CompetitorMap {
  version: string;
  ticker: string;
  direct_competitors: BusinessCompetitorItem[];
  similar_businesses: BusinessCompetitorItem[];
  related_businesses: BusinessCompetitorItem[];
  transparency: {
    methodology: string;
    data_boundary: string;
    not_recommendation: string;
  };
}

export interface IndustryIntelligence {
  version: string;
  industry: string;
  description: string;
  typical_characteristics: string[];
  common_risks: string[];
  common_opportunities: string[];
  economic_sensitivity: string;
  cycle_profile: string;
  educational_summary: string;
  companies: Array<{ ticker: string; name: string; sector: string; reason: string }>;
  learn_next: LearnNextTopic[];
  related_industries: string[];
  transparency: {
    methodology: string;
    data_boundary: string;
  };
}

export interface BusinessIntelligence {
  version: string;
  ticker: string;
  company_name: string;
  business_summary: {
    summary: string;
    why_investguide_thinks_this: string[];
  };
  business_model: {
    how_it_makes_money: string;
    main_products_services: string[];
    primary_customers: string;
    distribution_model: string;
    why_investguide_thinks_this: string[];
  };
  revenue_drivers: BusinessDriver[];
  competitive_position: {
    label: "Market Leader" | "Strong Competitor" | "Emerging Player" | "Niche Player";
    confidence: "Low" | "Medium" | "High";
    reasons: string[];
  };
  industry_position: {
    industry: string;
    summary: string;
    peer_count: number;
    why_investguide_thinks_this: string[];
  };
  business_maturity: {
    label: "Early Growth" | "Growth" | "Mature" | "Mature with Stable Cash Flows" | "Transitional";
    confidence: "Low" | "Medium" | "High";
    reason: string;
  };
  geographic_exposure: {
    primary_country: string;
    headquarters: string;
    summary: string;
    why_investguide_thinks_this: string[];
  };
  operational_risks: BusinessDriver[];
  industry_intelligence: IndustryIntelligence;
  competitors: CompetitorMap;
  knowledge_graph: KnowledgeGraphPayload;
  educational_notes: Array<{ title: string; note: string }>;
  transparency: {
    methodology: string;
    data_boundary: string;
    not_advice: string;
  };
  generated_at: string;
}
export interface CompanyDetail {
  company: Company;
  related_assets: Asset[];
  latest_news: NewsArticle[];
  assessment_available: boolean;
}

// ============================================================================
// Sentiment Types
// ============================================================================

export interface SentimentAnalysis {
  sentiment_score: number;
  sentiment_label: SentimentLabel;
  confidence_score: number;
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
  performance_score: number;
  risk_score: number;
  momentum_score: number;
  dividend_stability: number;
  volatility: number;
  risk_level: RiskLevel;
  liquidity_score: number;
}

export interface RecommendationScore {
  final_score: number;
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
  title: string;
  summary?: string | null;
  content?: string | null;
  content_hash?: string | null;
  source: string;
  author?: string | null;
  published_at: string;
  url?: string | null;
  image_url?: string | null;
  language: string;
  sentiment?: number | string | null;
  relevance_score?: number | string | null;
  credibility_score?: number | string | null;
  asset_tickers: string[];
  created_at: string;
  updated_at?: string;
}

export interface NewsEventCategory {
  label: string;
  reasons: string[];
}

export interface NewsImportance {
  label: "Low" | "Medium" | "High";
  score: number;
  reasons: string[];
}

export interface NewsSourceQuality {
  tier: string;
  label: string;
  score: number;
  reason: string;
}

export interface NewsEvidence {
  source_quality: NewsSourceQuality;
  data_completeness: number;
  confidence: "Low" | "Medium" | "High";
  why_confidence: string[];
  data_used: string[];
  missing_data: string[];
}

export interface NewsRelatedCompany {
  ticker: string;
  name: string;
  sector: string;
  reason: string;
}

export interface NewsResearch {
  article_id: number;
  title: string;
  summary?: string | null;
  event_category: NewsEventCategory;
  importance: NewsImportance;
  evidence: NewsEvidence;
  why_it_matters: string;
  explain_like_im_18: string;
  related_companies: NewsRelatedCompany[];
  related_sectors: string[];
  related_asset_types: string[];
  related_topics: string[];
  learn_next: LearnNextTopic[];
  knowledge_graph: KnowledgeGraphPayload;
  transparency: {
    methodology: string;
    not_advice: string;
  };
  generated_at: string;
  engine_version: string;
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
  indicator_name: string;
  indicator_value: number;
  indicator_unit: string;
  source: "RBZ" | "ZIMSTAT";
  reporting_date: string;
  category: "monetary" | "fiscal" | "commodity";
  created_at: string;
  updated_at?: string;
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
// User, Authentication & Personalization Types
// ============================================================================

export type RiskProfile = "conservative" | "moderate" | "aggressive";
export type ExperienceLevel = "beginner" | "intermediate" | "advanced";
export type PreferredLanguageLevel = "simple" | "balanced" | "technical";

export interface User {
  id: number;
  email: string;
  username?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: "bearer";
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface SignupResponse {
  user: User;
  access_token: string;
  token_type: "bearer";
}

export interface InvestorProfile {
  id: number;
  user_id?: number | null;
  experience_level: ExperienceLevel;
  risk_appetite: RiskProfile;
  investment_horizon?: string | null;
  planned_investment_range?: string | null;
  preferred_asset_types: string[];
  investment_goals: string[];
  preferred_language_level: PreferredLanguageLevel;
  education_focus: string[];
  created_at: string;
  updated_at: string;
}

export interface InvestorProfilePayload {
  experience_level?: ExperienceLevel;
  risk_appetite?: RiskProfile;
  investment_horizon?: string | null;
  planned_investment_range?: string | null;
  preferred_asset_types?: string[];
  investment_goals?: string[];
  preferred_language_level?: PreferredLanguageLevel;
  education_focus?: string[];
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  tokens: AuthTokens | null;
  investorProfile: InvestorProfile | null;
  onboardingComplete: boolean;
  hydrated: boolean;
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
  updated_at?: string;
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
  updated_at?: string;
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


