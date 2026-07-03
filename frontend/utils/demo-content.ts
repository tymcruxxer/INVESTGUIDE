import type { Asset, Company, InvestorProfile } from "@/types";

export interface DemoNewsItem {
  id: number;
  title: string;
  source: string;
  published_at: string;
  summary: string;
  asset_tickers: string[];
}

export const DEMO_ASSETS: Asset[] = [
  {
    id: 1,
    ticker: "DLTA",
    company_name: "Delta Corporation Limited",
    exchange: "ZSE",
    sector: "Consumer Staples",
    industry: "Beverages",
    asset_type: "equity",
    currency: "ZWG",
    description: "Delta is a leading Zimbabwean consumer group with strong brands and broad distribution reach.",
    market_cap: 1400000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    ticker: "ECO",
    company_name: "Econet Wireless Zimbabwe Limited",
    exchange: "ZSE",
    sector: "Telecommunications",
    industry: "Mobile Telecommunications",
    asset_type: "equity",
    currency: "ZWG",
    description: "Econet operates one of the largest telecommunications networks in Zimbabwe and is a key market bellwether.",
    market_cap: 1800000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 3,
    ticker: "INN",
    company_name: "Innscor Africa Limited",
    exchange: "ZSE",
    sector: "Consumer Staples",
    industry: "Food Production",
    asset_type: "equity",
    currency: "ZWG",
    description: "Innscor gives investors exposure to consumer staples, food manufacturing, and regional demand trends.",
    market_cap: 1250000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 4,
    ticker: "TIGZ",
    company_name: "Tigere Real Estate Investment Trust",
    exchange: "ZSE",
    sector: "Real Estate",
    industry: "REIT",
    asset_type: "REIT",
    currency: "ZWG",
    description: "Tigere REIT offers exposure to income-producing property assets and distribution yields.",
    market_cap: 650000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 5,
    ticker: "CMCL",
    company_name: "Caledonia Mining Corporation Plc",
    exchange: "VFEX",
    sector: "Basic Materials",
    industry: "Gold Mining",
    asset_type: "equity",
    currency: "USD",
    description: "Caledonia is a gold producer with exposure to global commodity cycles and foreign-currency dynamics.",
    market_cap: 900000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 6,
    ticker: "TBILL",
    company_name: "Treasury Bills",
    exchange: "ZSE",
    sector: "Government",
    industry: "Fixed Income",
    asset_type: "bond",
    currency: "ZWG",
    description: "Treasury Bills are short-term government instruments used for capital preservation and liquidity planning.",
    market_cap: 5000000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
];

export const DEMO_COMPANIES: Company[] = DEMO_ASSETS.filter((asset) => asset.asset_type !== "bond").map((asset) => ({
  id: asset.id,
  name: asset.company_name,
  legal_name: asset.company_name,
  ticker: asset.ticker,
  exchange: asset.exchange,
  sector: asset.sector,
  industry: asset.industry,
  country: "Zimbabwe",
  headquarters: asset.ticker === "CMCL" ? "Jersey / Zimbabwe operations" : "Harare",
  website: asset.official_website ?? null,
  description: asset.description,
  founded_year: asset.ticker === "DLTA" ? 1946 : null,
  employee_count: null,
  market: asset.exchange,
  currency: asset.currency,
  status: asset.status,
  logo_url: asset.logo_url ?? null,
  created_at: asset.created_at,
  updated_at: asset.updated_at,
}));

export const COMPANY_SLUGS: Record<string, string> = {
  delta: "DLTA",
  dlta: "DLTA",
  econet: "ECO",
  eco: "ECO",
  innscor: "INN",
  inn: "INN",
  tigere: "TIGZ",
  tigz: "TIGZ",
  caledonia: "CMCL",
  cmcl: "CMCL",
};

export function resolveCompanyTicker(slug: string) {
  const normalized = slug.trim().toLowerCase();
  return COMPANY_SLUGS[normalized] ?? slug.trim().toUpperCase();
}
export const DEMO_NEWS: DemoNewsItem[] = [
  {
    id: 1,
    title: "Sample: ZSE market liquidity watch for retail investors",
    source: "InvestGuide Sample Data",
    published_at: "2026-06-25T08:00:00Z",
    summary: "Development placeholder discussing how investors might monitor turnover, breadth, and liquidity on the ZSE.",
    asset_tickers: [],
  },
  {
    id: 2,
    title: "Sample: Delta Corporation company-news placeholder",
    source: "InvestGuide Sample Data",
    published_at: "2026-06-24T12:00:00Z",
    summary: "Development placeholder for future Delta-related news, filings, or analyst commentary.",
    asset_tickers: ["DLTA"],
  },
  {
    id: 3,
    title: "Sample: REIT income themes for Zimbabwean investors",
    source: "InvestGuide Sample Data",
    published_at: "2026-06-23T08:30:00Z",
    summary: "Development placeholder covering REIT education and income-focused monitoring themes.",
    asset_tickers: ["TIGZ"],
  },
];

export const ANALYTICS_PLACEHOLDERS = [
  { key: "quality_score", label: "Quality Score" },
  { key: "growth_score", label: "Growth Score" },
  { key: "value_score", label: "Value Score" },
  { key: "risk_score", label: "Risk Score" },
  { key: "liquidity_score", label: "Liquidity Score" },
  { key: "dividend_score", label: "Dividend Score" },
  { key: "macro_score", label: "Macro Score" },
  { key: "confidence_score", label: "Confidence Score" },
];

export function buildRoadmap(profile: InvestorProfile | null | undefined) {
  const goals = profile?.investment_goals ?? [];
  const horizon = profile?.investment_horizon ?? "long_term";
  const roadmap = [
    "Build an emergency fund before taking on more risk",
    "Start a monthly investing habit with a small, repeatable amount",
  ];

  if (goals.includes("passive_income") || goals.includes("diversification")) {
    roadmap.push("Diversify across income and growth-oriented assets");
  } else {
    roadmap.push("Diversify your portfolio across sectors and asset types");
  }

  if (horizon.includes("long") || horizon.includes("retirement")) {
    roadmap.push("Review your investments and goals quarterly so compounding stays on track");
  } else {
    roadmap.push("Review your positions regularly and adjust as circumstances change");
  }

  return roadmap;
}

export function buildRecommendedAssets(profile: InvestorProfile | null | undefined, assets: Asset[]) {
  const catalog = assets.length > 0 ? assets : DEMO_ASSETS;
  const risk = profile?.risk_appetite ?? "moderate";
  const preferred = new Set((profile?.preferred_asset_types ?? []).map((item) => item.toLowerCase()));
  const goals = new Set((profile?.investment_goals ?? []).map((item) => item.toLowerCase()));

  const scored = catalog.map((asset) => {
    let score = 0;
    const type = asset.asset_type.toLowerCase();
    const sector = asset.sector.toLowerCase();
    if (preferred.has(type) || preferred.has(asset.exchange.toLowerCase()) || preferred.has(sector)) score += 3;
    if (risk === "conservative" && (type === "reit" || type === "bond" || sector.includes("government"))) score += 3;
    if (risk === "moderate" && (type === "reit" || sector.includes("consumer") || sector.includes("financial"))) score += 2;
    if (risk === "aggressive" && (asset.exchange === "VFEX" || sector.includes("mining") || sector.includes("telecommunications"))) score += 3;
    if (goals.has("passive_income") && (type === "reit" || type === "bond")) score += 2;
    if (goals.has("growth") && type === "equity") score += 2;
    return { asset, score };
  });

  return scored
    .sort((left, right) => right.score - left.score || left.asset.company_name.localeCompare(right.asset.company_name))
    .slice(0, 4)
    .map(({ asset }) => asset);
}

export function getRecommendationReason(asset: Asset, profile: InvestorProfile | null | undefined) {
  const risk = profile?.risk_appetite ?? "moderate";
  if (asset.asset_type === "REIT") return "REIT exposure can suit investors who want income themes and diversification.";
  if (asset.asset_type === "bond") return "Fixed-income instruments can suit capital preservation and liquidity planning.";
  if (risk === "aggressive" && asset.exchange === "VFEX") return "VFEX exposure may appeal to investors comfortable with USD-linked growth themes.";
  if (asset.sector.toLowerCase().includes("consumer")) return "Consumer-facing businesses can be easier for beginners to understand and monitor.";
  return "This asset matches your profile or adds useful market coverage for comparison.";
}

export function getEducationSummary(asset: Asset) {
  if (asset.asset_type === "REIT") return "REITs can provide income, but property values and occupancy trends still matter.";
  if (asset.asset_type === "bond") return "Bonds are often used for capital preservation and predictable cash flows.";
  return "Equities can offer growth potential, but individual company performance and risk still matter.";
}

export function getExplainLikeIm18(asset: Asset) {
  return [
    `What ${asset.company_name} does: ${asset.description}`,
    "Why investors buy it: they want exposure to a business with a clear market role and growth potential.",
    "What could go wrong: company-specific setbacks, market conditions, or changes in earnings expectations.",
    "Typical holding period: long enough to let business progress matter more than short-term market noise.",
    "Beginner explanation: think of it as owning a piece of a business, not just a ticker symbol.",
  ];
}

export function getPersonalizationCopy(profile: InvestorProfile | null | undefined) {
  const experience = profile?.experience_level ?? "beginner";

  if (experience === "advanced") {
    return {
      tone: "technical",
      intro: "Your dashboard is concise and data-minded, with ticker, exchange, sector, and methodology context visible.",
      helper: "Advanced mode keeps educational notes available while surfacing more market terminology.",
    };
  }

  if (experience === "intermediate") {
    return {
      tone: "balanced",
      intro: "Your dashboard stays practical and clear, with enough context to compare choices responsibly.",
      helper: "You will see plain-language explanations alongside the core market details.",
    };
  }

  return {
    tone: "simple",
    intro: "Your dashboard uses plain English so the market feels easier to understand.",
    helper: "You will see beginner-friendly explanations and a lighter dose of jargon.",
  };
}