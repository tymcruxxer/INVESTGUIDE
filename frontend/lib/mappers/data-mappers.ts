import type { Asset, Company, CompanyProfile, CompanyProfileVerification, NewsArticle } from "@/types";

export interface BackendAssetLike {
  id?: number;
  ticker?: string;
  company_name?: string;
  exchange?: string;
  sector?: string | null;
  industry?: string | null;
  asset_type?: string;
  currency?: string;
  description?: string | null;
  logo_url?: string | null;
  official_website?: string | null;
  market_cap?: number | string | null;
  listing_date?: string | null;
  status?: string;
  created_at?: string;
  updated_at?: string;
}
export interface BackendCompanyLike {
  id?: number;
  name?: string;
  legal_name?: string | null;
  ticker?: string;
  exchange?: string;
  sector?: string | null;
  industry?: string | null;
  country?: string | null;
  headquarters?: string | null;
  website?: string | null;
  description?: string | null;
  founded_year?: number | null;
  employee_count?: number | null;
  market?: string | null;
  currency?: string | null;
  status?: string;
  logo_url?: string | null;
  created_at?: string;
  updated_at?: string;
}


export interface BackendCompanyProfileLike {
  id?: number | null;
  company_id?: number | null;
  business_summary?: string | null;
  primary_business?: string | null;
  products_services?: string[] | null;
  industry?: string | null;
  sub_industry?: string | null;
  headquarters?: string | null;
  founded_year?: number | null;
  website?: string | null;
  email?: string | null;
  phone?: string | null;
  country?: string | null;
  exchange?: string | null;
  currency?: string | null;
  employees?: number | null;
  status?: string | null;
  research_status?: string | null;
  last_verified?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}
export interface BackendNewsLike {
  id?: number;
  title?: string;
  summary?: string | null;
  content?: string | null;
  source?: string;
  author?: string | null;
  published_at?: string;
  url?: string | null;
  image_url?: string | null;
  language?: string;
  sentiment?: number | string | null;
  relevance_score?: number | string | null;
  credibility_score?: number | string | null;
  asset_tickers?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface MappedNewsItem {
  id: number;
  title: string;
  source: string;
  published_at: string;
  summary: string;
  asset_tickers: string[];
  url?: string | null;
}

const toNumber = (value: number | string | null | undefined): number | undefined => {
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }
  return undefined;
};

export function mapAsset(asset: BackendAssetLike | null | undefined): Asset | null {
  if (!asset) return null;

  const ticker = typeof asset.ticker === "string" ? asset.ticker.trim().toUpperCase() : "";
  if (!ticker) return null;

  return {
    id: asset.id ?? 0,
    ticker,
    company_name: asset.company_name?.trim() || ticker,
    exchange: (asset.exchange ?? "ZSE") as Asset["exchange"],
    sector: asset.sector?.trim() || "General",
    industry: asset.industry?.trim() || "General",
    asset_type: (asset.asset_type ?? "equity") as Asset["asset_type"],
    currency: (asset.currency ?? "ZWG") as Asset["currency"],
    description: asset.description?.trim() || "No description available yet.",
    logo_url: asset.logo_url ?? undefined,
    official_website: asset.official_website ?? undefined,
    market_cap: toNumber(asset.market_cap),
    listing_date: asset.listing_date ?? undefined,
    status: (asset.status ?? "active") as Asset["status"],
    created_at: asset.created_at ?? new Date().toISOString(),
    updated_at: asset.updated_at,
  };
}

export function mapAssets(assets: BackendAssetLike[] | null | undefined): Asset[] {
  return (assets ?? []).map((asset) => mapAsset(asset)).filter((asset): asset is Asset => Boolean(asset));
}

export function mapCompany(company: BackendCompanyLike | null | undefined): Company | null {
  if (!company) return null;

  const ticker = typeof company.ticker === "string" ? company.ticker.trim().toUpperCase() : "";
  if (!ticker) return null;

  return {
    id: company.id ?? 0,
    name: company.name?.trim() || ticker,
    legal_name: company.legal_name ?? undefined,
    ticker,
    exchange: (company.exchange ?? "ZSE") as Company["exchange"],
    sector: company.sector?.trim() || "General",
    industry: company.industry?.trim() || "General",
    country: company.country?.trim() || "Zimbabwe",
    headquarters: company.headquarters ?? undefined,
    website: company.website ?? undefined,
    description: company.description?.trim() || "No company profile is available yet.",
    founded_year: company.founded_year ?? undefined,
    employee_count: company.employee_count ?? undefined,
    market: company.market ?? company.exchange ?? undefined,
    currency: (company.currency ?? undefined) as Company["currency"],
    status: (company.status ?? "active") as Company["status"],
    logo_url: company.logo_url ?? undefined,
    created_at: company.created_at ?? new Date().toISOString(),
    updated_at: company.updated_at,
  };
}

export function mapCompanies(companies: BackendCompanyLike[] | null | undefined): Company[] {
  return (companies ?? [])
    .map((company) => mapCompany(company))
    .filter((company): company is Company => Boolean(company));
}
export function mapCompanyProfile(profile: BackendCompanyProfileLike | null | undefined): CompanyProfile | null {
  if (!profile) return null;

  return {
    id: profile.id ?? null,
    company_id: profile.company_id ?? null,
    business_summary: profile.business_summary ?? null,
    primary_business: profile.primary_business ?? null,
    products_services: Array.isArray(profile.products_services) ? profile.products_services.filter(Boolean) : [],
    industry: profile.industry ?? null,
    sub_industry: profile.sub_industry ?? null,
    headquarters: profile.headquarters ?? null,
    founded_year: profile.founded_year ?? null,
    website: profile.website ?? null,
    email: profile.email ?? null,
    phone: profile.phone ?? null,
    country: profile.country ?? null,
    exchange: (profile.exchange ?? null) as CompanyProfile["exchange"],
    currency: (profile.currency ?? null) as CompanyProfile["currency"],
    employees: profile.employees ?? null,
    status: (profile.status ?? null) as CompanyProfile["status"],
    research_status: (profile.research_status ?? "unavailable") as CompanyProfile["research_status"],
    last_verified: profile.last_verified ?? null,
    source_name: profile.source_name ?? null,
    source_url: profile.source_url ?? null,
    created_at: profile.created_at ?? null,
    updated_at: profile.updated_at ?? null,
  };
}

export function mapCompanyProfileVerification(
  verification: Partial<CompanyProfileVerification> | null | undefined
): CompanyProfileVerification {
  return {
    last_verified: verification?.last_verified ?? null,
    source_name: verification?.source_name ?? null,
    source_url: verification?.source_url ?? null,
    research_status: verification?.research_status ?? "unavailable",
  };
}
export function mapNewsArticle(article: BackendNewsLike | null | undefined): MappedNewsItem | null {
  if (!article) return null;

  return {
    id: article.id ?? 0,
    title: article.title?.trim() || "Untitled article",
    source: article.source?.trim() || "Unknown source",
    published_at: article.published_at ?? article.created_at ?? new Date().toISOString(),
    summary: article.summary?.trim() || article.content?.trim() || "No summary available yet.",
    asset_tickers: Array.isArray(article.asset_tickers)
      ? article.asset_tickers.map((ticker) => ticker.trim().toUpperCase()).filter(Boolean)
      : [],
    url: article.url,
  };
}

export function mapNewsArticles(articles: NewsArticle[] | BackendNewsLike[] | null | undefined): MappedNewsItem[] {
  return (articles ?? [])
    .map((article) => mapNewsArticle(article))
    .filter((article): article is MappedNewsItem => Boolean(article));
}

export function formatDisplayDate(value: string | null | undefined): string {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}