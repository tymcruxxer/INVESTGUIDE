const TICKER_ALIASES: Record<string, string> = {
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

export function normalizeTickerForApi(value: string | null | undefined): string {
  const raw = (value ?? "").trim();
  if (!raw) return "";
  const normalized = raw.toLowerCase();
  return TICKER_ALIASES[normalized] ?? raw.toUpperCase();
}

export function tickerToRoute(value: string | null | undefined): string {
  return normalizeTickerForApi(value).toLowerCase();
}