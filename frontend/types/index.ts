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

export interface FinancialRatio {
  name: string;
  value: number | null;
  interpretation: string;
  why_it_matters: string;
  educational_explanation: string;
}

export interface FinancialTrend {
  metric: string;
  direction: "Increasing" | "Stable" | "Declining" | "Mixed" | "Insufficient Data";
  values: Array<{ period: number | string | null; value: number | null }>;
  explanation: string;
  why_it_matters: string;
}

export interface FinancialHealth {
  label: "Excellent" | "Strong" | "Healthy" | "Moderate" | "Weak" | "Concerning";
  score: number;
  why: string;
  evidence: string[];
  cautions: string[];
  missing_data: string[];
  uncertainty: "Low" | "Medium" | "High";
}

export interface FinancialStatementRow {
  id: number;
  company_id: number;
  fiscal_year: number;
  period: string;
  currency?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  is_development_data: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  [key: string]: string | number | boolean | null | undefined;
}

export interface FinancialIntelligence {
  ticker: string;
  company_name: string;
  financial_health: FinancialHealth;
  revenue_analysis: {
    current_revenue: number | null;
    trend: string;
    explanation: string;
    why_it_matters: string;
  };
  profitability_analysis: {
    net_margin: FinancialRatio;
    operating_margin: FinancialRatio;
    net_profit_trend: FinancialTrend;
    explanation: string;
  };
  liquidity_analysis: {
    current_ratio: FinancialRatio;
    quick_ratio: FinancialRatio;
    working_capital: number | null;
    explanation: string;
  };
  leverage_analysis: {
    debt_to_equity: FinancialRatio;
    debt_ratio: FinancialRatio;
    total_debt: number | null;
    explanation: string;
  };
  cash_flow_analysis: {
    operating_cash_flow: number | null;
    free_cash_flow: number | null;
    operating_cash_flow_ratio: FinancialRatio;
    trend: FinancialTrend;
    explanation: string;
  };
  growth_characteristics: {
    label: string;
    revenue_trend: FinancialTrend;
    profit_trend: FinancialTrend;
    explanation: string;
  };
  stability_assessment: {
    label: string;
    watch_items: string[];
    explanation: string;
  };
  revenue_quality: {
    revenue_drivers: string[];
    revenue_concentration: string;
    recurring_vs_variable: string;
    business_stability: string;
    educational_explanation: string;
    current_revenue: number | null;
  };
  balance_sheet_intelligence: {
    assets: number | null;
    liabilities: number | null;
    equity: number | null;
    working_capital: number | null;
    liquidity: string;
    debt: string;
    financial_flexibility: string;
  };
  ratios: FinancialRatio[];
  trend_analysis: FinancialTrend[];
  educational_summary: string;
  explain_like_im_18: string;
  knowledge_graph: {
    nodes: Array<{ id: string; label: string; type: string }>;
    edges: Array<{ from: string; to: string; relationship: string }>;
  };
  transparency: {
    data_sources: string[];
    available_periods: string[];
    missing_data: string[];
    evidence_used: string[];
    last_updated?: string | null;
    development_data: boolean;
    methodology: string;
    not_advice: string;
    engine_version: string;
    methodology_version: string;
  };
  generated_at: string;
}

export interface CompanyFinancialsPayload {
  company: Company;
  income_statements: FinancialStatementRow[];
  balance_sheets: FinancialStatementRow[];
  cash_flow_statements: FinancialStatementRow[];
  intelligence: FinancialIntelligence;
}


export interface FinancialStatementSectionProvenance {
  source: string;
  reporting_period: string;
  verification_status: string;
  last_updated?: string | null;
}

export interface FinancialStatementIntelligenceSection {
  headline: string;
  value: number | null;
  trend: string;
  explanation: string;
  evidence: string[];
  confidence: "Low" | "Medium" | "High";
  provenance: FinancialStatementSectionProvenance;
  why_it_matters: string;
  explain_like_im_18: string;
  learn_next: string[];
}

export interface FinancialStatementIntelligence {
  ticker: string;
  company_name: string;
  statement_coverage: {
    income_statement_periods: number;
    balance_sheet_periods: number;
    cash_flow_periods: number;
    complete_latest_period: boolean;
  };
  available_reporting_periods: string[];
  missing_fields: string[];
  sections: Record<"revenue" | "profitability" | "liquidity" | "leverage" | "cash_flow" | "earnings_quality", FinancialStatementIntelligenceSection>;
  evidence: {
    confidence: "Low" | "Medium" | "High";
    confidence_reason: string;
    data_used: string[];
    missing_data: string[];
  };
  educational_layer: {
    why_financial_statements_matter: string;
    learn_next: string[];
    explain_like_im_18: string;
  };
  transparency: {
    source: string;
    sources: string[];
    reporting_period: string;
    verification_status: string;
    last_updated?: string | null;
    development_data: boolean;
    confidence: "Low" | "Medium" | "High";
    methodology: string;
    not_advice: string;
    engine_version: string;
    methodology_version: string;
    base_financial_engine_version: string;
    base_financial_methodology_version: string;
  };
  generated_at: string;
}

export interface CompanyFinancialStatementsPayload {
  company: Company;
  income_statements: FinancialStatementRow[];
  balance_sheets: FinancialStatementRow[];
  cash_flow_statements: FinancialStatementRow[];
  available_reporting_periods: string[];
  missing_fields: string[];
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
}

export interface CompanyFinancialStatementIntelligencePayload {
  company: Company;
  intelligence: FinancialStatementIntelligence;
}export interface CompanyFinancialHealthPayload {
  ticker: string;
  company_name: string;
  financial_health: FinancialHealth;
  ratios: FinancialRatio[];
  trend_analysis: FinancialTrend[];
  transparency: FinancialIntelligence["transparency"];
}
export interface DividendRecord {
  id: number;
  company_id: number;
  asset_id?: number | null;
  announcement_date?: string | null;
  record_date?: string | null;
  ex_dividend_date?: string | null;
  payment_date?: string | null;
  fiscal_year?: number | null;
  dividend_type: "Interim" | "Final" | "Special" | "Other";
  dividend_per_share?: number | null;
  currency?: string | null;
  shares_outstanding?: number | null;
  total_dividend_amount?: number | null;
  source_name?: string | null;
  source_type?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  verified_at?: string | null;
  is_development_data: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DividendMetric {
  status: string;
  value: number | null;
  period: number | null;
  interpretation: string;
  why_it_matters: string;
  missing_inputs: string[];
  limitations: string[];
}

export interface DividendIntelligence {
  ticker: string;
  company_name: string;
  dividend_status: {
    label: string;
    explanation: string;
    evidence_used: string[];
    missing_data: string[];
    confidence: "Low" | "Medium" | "High";
  };
  dividend_history: {
    periods: Array<{
      fiscal_year?: number | null;
      dividend_type?: string | null;
      dividend_per_share: number | null;
      currency?: string | null;
      announcement_date?: string | null;
      record_date?: string | null;
      ex_dividend_date?: string | null;
      payment_date?: string | null;
      total_dividend_amount: number | null;
    }>;
    annual_totals: Array<{
      fiscal_year: number;
      annual_dividend_per_share: number;
      total_dividend_amount: number;
      record_count: number;
      currency?: string | null;
    }>;
    periods_available: number;
    missing_periods: number[];
    trend_label: string;
    methodology: string;
  };
  dividend_yield: DividendMetric & {
    price_date?: string | null;
    dividend_period_used?: number | null;
    educational_explanation?: string;
  };
  payout_ratio: DividendMetric;
  cash_payout_ratio: DividendMetric;
  dividend_growth: {
    annual_growth: Array<{ from: number; to: number; growth: number }>;
    compound_annual_growth_rate: number | null;
    trend_label: string;
    explanation: string;
    confidence: "Low" | "Medium" | "High";
    missing_years: number[];
  };
  dividend_consistency: {
    label: string;
    periods_available: number;
    consecutive_periods: boolean;
    amount_variability: string;
    missing_periods: number[];
    explanation: string;
  };
  dividend_coverage: {
    profit_coverage: DividendMetric;
    cash_coverage: DividendMetric;
    summary: string;
  };
  sustainability_assessment: {
    score: number;
    label: string;
    supporting_evidence: string[];
    risks: string[];
    missing_data: string[];
    confidence: "Low" | "Medium" | "High";
    methodology: string;
  };
  key_risks: Array<{ risk: string; why_it_matters: string }>;
  educational_summary: string;
  explain_like_im_18: string;
  data_transparency: {
    data_sources: string[];
    available_periods: string[];
    missing_data: string[];
    development_data: boolean;
    evidence_used: string[];
    methodology: string;
    not_advice: string;
    engine_version: string;
    methodology_version: string;
  };
  suggested_learning_topics: string[];
  knowledge_graph: {
    nodes: Array<{ id: string; label: string; type: string }>;
    edges: Array<{ from: string; to: string; relationship: string }>;
  };
  generated_at: string;
  engine_version: string;
  methodology_version: string;
}

export interface CompanyDividendsPayload {
  company: Company;
  dividends: DividendRecord[];
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
}

export interface CompanyDividendIntelligencePayload {
  company: Company;
  dividends: DividendRecord[];
  intelligence: DividendIntelligence;
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


export interface AdminPermission {
  id: number;
  code: string;
  name: string;
  category: string;
  description?: string | null;
}

export interface AdminRole {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  is_system_role: boolean;
  is_owner_role: boolean;
  is_active: boolean;
  assigned_user_count?: number;
  permissions?: AdminPermission[];
}

export interface AdminMe {
  user: User;
  roles: AdminRole[];
  permissions: string[];
  is_owner: boolean;
  primary_role?: AdminRole | null;
  mode: "admin";
}

export interface AdminNavigationItem {
  label: string;
  href: string;
  permission: string;
}

export interface AdminNavigationPayload {
  items: AdminNavigationItem[];
  mode: "admin";
}

export interface AdminPermissionsPayload {
  permissions: AdminPermission[];
  grouped_permissions: Record<string, AdminPermission[]>;
  roles: AdminRole[];
  user_permissions: string[];
  owner_bypass: boolean;
  audit: Record<string, boolean>;
  sensitive_actions: Record<string, boolean>;
  generated_at: string;
  metadata: Record<string, unknown>;
}

export interface AdminUserSummary {
  id: number;
  email: string;
  username?: string | null;
  display_name?: string | null;
  roles: string[];
  is_active: boolean;
  is_verified: boolean;
  status: "active" | "suspended";
  created_at?: string | null;
  last_login_at?: string | null;
  suspended_at?: string | null;
  subscription_tier: string;
}

export interface AdminAuditSummaryItem {
  action: string;
  result: string;
  reason?: string | null;
  created_at?: string | null;
}

export interface AdminUserDetail extends AdminUserSummary {
  permissions: string[];
  activity_summary: Record<string, unknown>;
  audit_summary: AdminAuditSummaryItem[];
  suspension_reason?: string | null;
  restored_at?: string | null;
}

export interface AdminUserListPayload {
  users: AdminUserSummary[];
  total: number;
  page: number;
  limit: number;
}

export interface AdminRoleMutationPayload {
  role_id: number;
  action: "assign" | "remove";
  reason: string;
  confirmation: boolean;
}

export interface AdminUserStatusPayload {
  status: "active" | "suspended";
  reason: string;
  confirmation: boolean;
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





// ============================================================================
// Internal Data Operations Types
// ============================================================================

export interface QualityScorePayload {
  score: number;
  label: string;
  reasons: string[];
}

export interface FreshnessPayload {
  latest_update?: string | null;
  target_days: number;
  age_days?: number | null;
  status: string;
  score: QualityScorePayload;
  explanation: string;
}

export interface IngestionRunSummary {
  id: number;
  entity: string;
  mode: string;
  status: string;
  source_name: string;
  source_type: string;
  source_url?: string | null;
  dataset_version?: string | null;
  checksum?: string | null;
  verification_status: string;
  is_development_data: boolean;
  triggered_by?: string | null;
  started_at: string;
  completed_at?: string | null;
  duration_ms?: number | null;
  received_count: number;
  normalized_count: number;
  valid_count: number;
  inserted_count: number;
  updated_count: number;
  skipped_count: number;
  rejected_count: number;
  warning_count: number;
  error_count: number;
  error_summary?: string | null;
  warning_summary?: string | null;
}

export interface IngestionRecordIssue {
  id: number;
  ingestion_run_id: number;
  entity_type: string;
  record_index?: number | null;
  external_key?: string | null;
  severity: string;
  issue_code: string;
  field_name?: string | null;
  message: string;
  raw_value_summary?: string | null;
  created_at?: string | null;
}

export interface SourceHealthPayload {
  source_name: string;
  source_type: string;
  last_successful_run?: string | null;
  last_failed_run?: string | null;
  success_rate: number;
  recent_rejected_record_count: number;
  recent_warning_count: number;
  average_run_duration_ms?: number | null;
  latest_dataset_version?: string | null;
  latest_checksum?: string | null;
  freshness_status: string;
  current_health: string;
}

export interface EntityQualityPayload {
  entity_type: string;
  total_records: number;
  verified_records: number;
  development_records: number;
  unverified_records: number;
  latest_import?: string | null;
  latest_verified_update?: string | null;
  quality_score: QualityScorePayload;
  completeness: QualityScorePayload;
  validity: QualityScorePayload;
  provenance: QualityScorePayload;
  freshness: FreshnessPayload;
  consistency: QualityScorePayload;
  freshness_status: string;
  open_warning_count: number;
  open_rejection_count: number;
  source_count: number;
}

export interface DataQualitySummaryPayload {
  pipeline_health: string;
  latest_ingestion_run?: IngestionRunSummary | null;
  verified_record_count: number;
  development_record_count: number;
  stale_dataset_count: number;
  rejected_record_count: number;
  entities: EntityQualityPayload[];
}

export interface IngestionRunDetailPayload {
  run: IngestionRunSummary;
  issue_code_distribution: Record<string, number>;
  retry_guidance: string[];
}

export interface CompanyDataQualityPayload {
  ticker: string;
  company_name: string;
  components: Record<string, QualityScorePayload | FreshnessPayload>;
  development_data_present: boolean;
  missing_critical_fields: string[];
  news_coverage: { linked_articles: number };
  suggested_operator_actions: string[];
  provenance_status: string;
}

export interface MacroIndicatorRecord {
  id: number;
  indicator_type: "inflation" | "interest_rate" | "exchange_rate" | "gdp" | "commodity_price";
  name: string;
  value: number;
  unit: string;
  reporting_period: string;
  country: string;
  currency?: string | null;
  commodity?: string | null;
  notes?: string | null;
  source_name?: string | null;
  source_type?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  verified_at?: string | null;
  verification_status?: string | null;
  dataset_version?: string | null;
  is_development_data: boolean;
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
  created_at?: string | null;
  updated_at?: string | null;
}

export interface MacroEvidence {
  confidence: "Low" | "Medium" | "High";
  source_quality: string;
  data_completeness: number;
  data_used: string[];
  missing_data: string[];
  why_confidence: string[];
}

export interface MacroCompanyImpactItem {
  indicator_type: string;
  label: string;
  why_it_matters: string;
  relationship_chain: string[];
  explanation: string;
  not_prediction: string;
}

export interface MacroRelatedCompany {
  ticker: string;
  name: string;
  sector: string;
  reason: string;
  href: string;
}

export interface MacroResearchPayload {
  indicator_type: string;
  label: string;
  current_value?: MacroIndicatorRecord | null;
  historical_availability: {
    records_available: number;
    periods: string[];
  };
  overview: string;
  why_investors_care: string;
  typical_business_impacts: string[];
  typical_sector_impacts: string[];
  evidence: MacroEvidence;
  explain_like_im_18: string;
  affected_sectors: Array<{ sector: string; reason: string }>;
  affected_companies: MacroRelatedCompany[];
  knowledge_graph: KnowledgeGraphPayload;
  learn_next: LearnNextTopic[];
  transparency: {
    methodology: string;
    data_origin: string;
    not_advice: string;
  };
  generated_at: string;
  engine_version: string;
}

export interface MacroIndicatorPayload {
  indicator_type: string;
  records: MacroIndicatorRecord[];
  latest?: MacroIndicatorRecord | null;
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
}

export interface MacroOverviewPayload {
  indicators: MacroIndicatorRecord[];
  research: MacroResearchPayload[];
  transparency: {
    methodology: string;
    not_advice: string;
  };
  generated_at: string;
  engine_version: string;
}

export interface CompanyMacroImpactPayload {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  factors: MacroCompanyImpactItem[];
  knowledge_graph: KnowledgeGraphPayload;
  transparency: {
    methodology: string;
    data_points_seen: number;
    not_advice: string;
  };
  generated_at: string;
  engine_version: string;
}

// ============================================================================
// Sector and Industry Intelligence Types
// ============================================================================

export interface SectorSummary {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  country: string;
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
}

export interface IndustrySummary {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  sector_id: number;
  data_origin: "Development Preview" | "Persisted Backend" | "Unavailable";
}

export interface SectorRecord extends SectorSummary {
  exchange_coverage?: string | null;
  overview?: string | null;
  source_name?: string | null;
  source_type?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  verified_at?: string | null;
  verification_status: string;
  dataset_version?: string | null;
  is_development_data: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  industries: IndustrySummary[];
}

export interface IndustryRecord extends IndustrySummary {
  sector: SectorSummary;
  overview?: string | null;
  source_name?: string | null;
  source_type?: string | null;
  source_url?: string | null;
  imported_at?: string | null;
  verified_at?: string | null;
  verification_status: string;
  dataset_version?: string | null;
  is_development_data: boolean;
  created_at?: string | null;
  updated_at?: string | null;
  companies?: SectorCompanyItem[];
}

export interface SectorCompanyItem {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  exchange: string;
  href: string;
  reason: string;
}

export interface SectorResearchPayload {
  version: string;
  sector: SectorRecord;
  overview: {
    what_it_is: string;
    typical_businesses: string[];
    why_investors_study_it: string;
  };
  typical_characteristics: string[];
  typical_opportunities: Array<{ label: string; why_it_matters: string }>;
  typical_risks: Array<{ label: string; why_it_matters: string }>;
  macro_relationships: Array<{ indicator_type: string; label: string; relationship: string; path: string }>;
  financial_characteristics: string[];
  industries: IndustrySummary[];
  companies: SectorCompanyItem[];
  related_sectors: Array<{ name: string; reason: string }>;
  evidence: {
    evidence_strength: string;
    available_data: string[];
    missing_data: string[];
    transparency: string;
  };
  knowledge_graph: KnowledgeGraphPayload;
  learn_next: LearnNextTopic[];
  transparency: {
    source_name?: string | null;
    source_url?: string | null;
    verification_status: string;
    data_origin: string;
    methodology: string;
    not_advice: string;
  };
  generated_at: string;
}

export interface IndustryResearchPayload {
  version: string;
  industry: {
    id: number;
    name: string;
    slug: string;
    description?: string | null;
    overview?: string | null;
    data_origin: string;
  };
  sector: {
    name: string;
    slug: string;
    description?: string | null;
  };
  overview: string;
  typical_business_model: string;
  macro_exposure: Array<{ indicator_type: string; label: string; relationship: string; path: string }>;
  typical_risks: Array<{ label: string; why_it_matters: string }>;
  typical_opportunities: Array<{ label: string; why_it_matters: string }>;
  related_companies: SectorCompanyItem[];
  learn_next: LearnNextTopic[];
  knowledge_graph: KnowledgeGraphPayload;
  transparency: SectorResearchPayload["transparency"];
  generated_at: string;
}

export interface SectorDetailPayload {
  sector: SectorRecord;
  companies: SectorCompanyItem[];
  industry_count: number;
  company_count: number;
}





