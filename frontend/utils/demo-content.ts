import type { Asset, InvestorProfile } from "@/types";

export interface DemoNewsItem {
  id: number;
  title: string;
  source: string;
  published_at: string;
  summary: string;
  asset_ticker?: string;
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
    ticker: "CMCL",
    company_name: "Caledonia Mining Corporation Plc",
    exchange: "VFEX",
    sector: "Basic Materials",
    industry: "Gold Mining",
    asset_type: "equity",
    currency: "USD",
    description: "Caledonia is a mid-tier gold producer with exposure to global commodity cycles and FX dynamics.",
    market_cap: 900000000,
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
    ticker: "TRB",
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
  {
    id: 6,
    ticker: "MMF",
    company_name: "Money Market Fund",
    exchange: "ZSE",
    sector: "Financials",
    industry: "Money Market",
    asset_type: "bond",
    currency: "ZWG",
    description: "A low-volatility cash management option for investors prioritizing stability and predictable access.",
    market_cap: 1200000000,
    status: "active",
    created_at: "2024-01-01T00:00:00Z",
  },
];

export const DEMO_NEWS: DemoNewsItem[] = [
  {
    id: 1,
    title: "Local equities steady as inflation expectations cool",
    source: "Bloomberg Lite",
    published_at: "2026-07-01",
    summary: "Market participants are watching rate signals and company earnings as the local market stabilizes.",
    asset_ticker: "DLTA",
  },
  {
    id: 2,
    title: "REITs gain attention from income-focused investors",
    source: "InvestGuide Desk",
    published_at: "2026-06-30",
    summary: "Distribution yield and portfolio diversification continue to attract cautious investors.",
    asset_ticker: "TIGZ",
  },
  {
    id: 3,
    title: "Gold miners remain in focus as US dollar demand strengthens",
    source: "Market Brief",
    published_at: "2026-06-29",
    summary: "Mining names are supported by commodity demand and investor appetite for inflation hedges.",
    asset_ticker: "CMCL",
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

export function buildRecommendedAssets(profile: InvestorProfile | null | undefined) {
  const risk = profile?.risk_appetite ?? "moderate";
  const goals = profile?.investment_goals ?? [];

  if (risk === "conservative" || goals.includes("capital_preservation")) {
    return [DEMO_ASSETS[4], DEMO_ASSETS[5], DEMO_ASSETS[3]];
  }

  if (risk === "aggressive") {
    return [DEMO_ASSETS[2], DEMO_ASSETS[0], DEMO_ASSETS[1]];
  }

  return [DEMO_ASSETS[0], DEMO_ASSETS[3], DEMO_ASSETS[2]];
}

export function getEducationSummary(asset: Asset) {
  if (asset.asset_type === "REIT") {
    return "REITs can provide income, but property values and occupancy trends still matter.";
  }
  if (asset.asset_type === "bond") {
    return "Bonds are often used for capital preservation and predictable cash flows.";
  }
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
      intro: "Your profile is set up for more detail, so the dashboard stays concise and data-minded.",
      helper: "You can expect ticker-level context, exchange context, and sector framing.",
    };
  }

  if (experience === "intermediate") {
    return {
      tone: "balanced",
      intro: "Your dashboard stays practical and clear, with enough context to help you compare choices.",
      helper: "You will see plain-language explanations alongside the core market details.",
    };
  }

  return {
    tone: "simple",
    intro: "Your dashboard uses plain English so the market feels easier to understand.",
    helper: "You will see beginner-friendly explanations and a lighter dose of jargon.",
  };
}
