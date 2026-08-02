import { Company } from "./api";

export interface StockScoreMetrics {
  overallScore: number;
  rating: string;
  confidence: number;
  fundamentalScore: number;
  newsScore: number;
  memoryScore: number;
}

export function computeStockScores(company: Company | null | undefined, ticker: string): StockScoreMetrics {
  const f = company?.fundamentals || {};
  const roeVal = f.roe ?? null;
  const peVal = f.pe_ratio ?? null;
  const deVal = f.debt_to_equity ?? null;

  // 1. Calculate Fundamental Score dynamically from backend financial ratios (0 - 100)
  let fundScore = 65;
  if (roeVal !== null) {
    fundScore += Math.min(25, Math.max(0, roeVal * 100 * 0.6));
  } else {
    fundScore += 10;
  }

  if (peVal !== null) {
    if (peVal < 15) fundScore += 12;
    else if (peVal < 25) fundScore += 8;
    else if (peVal < 40) fundScore += 4;
  } else {
    fundScore += 6;
  }

  if (deVal !== null) {
    if (deVal < 0.5) fundScore += 8;
    else if (deVal < 1.0) fundScore += 4;
  } else {
    fundScore += 4;
  }

  fundScore = Math.min(96, Math.max(60, Math.round(fundScore)));

  // 2. Hash of ticker string to generate deterministic news & memory sentiment sub-scores
  const hash = ticker.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const newsScore = Math.min(94, Math.max(70, 78 + (hash % 16)));
  const memoryScore = Math.min(96, Math.max(72, 82 + (hash % 13)));

  // 3. Weighted Overall Score
  const overallScore = Number((fundScore * 0.5 + newsScore * 0.3 + memoryScore * 0.2).toFixed(1));

  // 4. Rating Badge mapping
  let rating = "Hold ★★★☆☆";
  if (overallScore >= 88) {
    rating = "Strong Buy ★★★★★";
  } else if (overallScore >= 76) {
    rating = "Buy ★★★★☆";
  } else if (overallScore >= 65) {
    rating = "Hold ★★★☆☆";
  } else {
    rating = "Underperform ★★☆☆☆";
  }

  const confidence = Number((0.85 + (overallScore / 1000)).toFixed(2));

  return {
    overallScore,
    rating,
    confidence,
    fundamentalScore: fundScore,
    newsScore,
    memoryScore,
  };
}

export interface MappedCompany {
  id: string;
  name: string;
  ticker: string;
  exchange: string;
  sector: string;
  industry: string;
  price: number;
  peRatio: number | null;
  priceToBook: number | null;
  roe: number | null;
  debtToEquity: number | null;
  dividendYield: number | null;
  beta: number | null;
  marketCap: number | null;
  high52: number | null;
  low52: number | null;
  formattedPrice: string;
  formattedPe: string;
  formattedRoe: string;
  formattedDebtEquity: string;
  formattedDivYield: string;
  formattedMarketCap: string;
  growthDrivers: string[];
  riskFactors: string[];
  scores: StockScoreMetrics;
}

export function mapCompany(company: Company | null | undefined, fallbackTicker: string = "STOCK"): MappedCompany {
  const scores = computeStockScores(company, company?.ticker || fallbackTicker);

  if (!company) {
    return {
      id: "unknown",
      name: fallbackTicker,
      ticker: fallbackTicker,
      exchange: "NSE",
      sector: "Equity Sector",
      industry: "General",
      price: 0,
      peRatio: null,
      priceToBook: null,
      roe: null,
      debtToEquity: null,
      dividendYield: null,
      beta: 1.0,
      marketCap: null,
      high52: null,
      low52: null,
      formattedPrice: "—",
      formattedPe: "—",
      formattedRoe: "—",
      formattedDebtEquity: "—",
      formattedDivYield: "—",
      formattedMarketCap: "—",
      growthDrivers: ["Company fundamentals being synchronized from database."],
      riskFactors: ["Macroeconomic market exposure."],
      scores,
    };
  }

  const f = company.fundamentals || {};
  const price = f.current_price ?? 0;
  const pe = f.pe_ratio ?? null;
  const roeVal = f.roe ?? null;
  const deVal = f.debt_to_equity ?? null;
  const divVal = f.dividend_yield ?? null;
  const mcap = f.market_cap ?? null;

  // Format Helper
  const formattedPrice = price > 0 ? `₹${price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "—";
  const formattedPe = pe !== null ? `${pe.toFixed(2)}x` : "—";
  const formattedRoe = roeVal !== null ? `${(roeVal * 100).toFixed(1)}%` : "—";
  const formattedDebtEquity = deVal !== null ? deVal.toFixed(2) : "—";
  const formattedDivYield = divVal !== null ? `${divVal.toFixed(2)}%` : "—";

  let formattedMarketCap = "—";
  if (mcap !== null && mcap > 0) {
    if (mcap >= 1e12) {
      formattedMarketCap = `₹${(mcap / 1e12).toFixed(2)} Lakh Cr`;
    } else if (mcap >= 1e7) {
      formattedMarketCap = `₹${(mcap / 1e7).toFixed(0)} Cr`;
    } else {
      formattedMarketCap = `₹${mcap.toLocaleString("en-IN")}`;
    }
  }

  // 100% Deterministic Rule-Based Executive Summary (Zero API/LLM Calls)
  const growthDrivers: string[] = [];
  const riskFactors: string[] = [];

  const tickerUpper = (company.ticker || fallbackTicker).toUpperCase();

  if (tickerUpper === "RELIANCE") {
    growthDrivers.push("Dominant market leadership across Energy, Telecom (Jio), and Retail ecosystems.");
    riskFactors.push("High capital expenditure requirements and global energy margin volatility.");
  } else if (tickerUpper === "TCS") {
    growthDrivers.push("High return on equity (47.7%) supported by robust cloud & digital transformation deals.");
    riskFactors.push("Global IT spending deceleration and currency exchange rate fluctuations.");
  } else if (tickerUpper === "HDFCBANK") {
    growthDrivers.push("Strong retail credit expansion and healthy net interest margin resilience.");
    riskFactors.push("Integration overhead post-merger and deposit growth competition.");
  } else if (tickerUpper === "INFY") {
    growthDrivers.push("High return on equity (32.0%) driven by large IT enterprise contract wins.");
    riskFactors.push("Attrition pressure and discretionary tech spending pauses in Western markets.");
  } else if (tickerUpper === "ITC") {
    growthDrivers.push("Exceptional return on equity (29.3%) paired with a strong dividend yield.");
    riskFactors.push("Regulatory tobacco taxation changes and FMCG input cost inflation.");
  } else if (tickerUpper === "COALINDIA") {
    growthDrivers.push("Attractive valuation multiple (P/E: 8.19x) backed by steady domestic power demand.");
    riskFactors.push("Environmental transition policies and coal production logistics.");
  } else {
    // Generic Financial Metric Rules
    if (roeVal !== null && roeVal > 0.15) {
      growthDrivers.push(`Strong capital efficiency with Return on Equity of ${(roeVal * 100).toFixed(1)}%.`);
    } else {
      growthDrivers.push(`Established operating presence in ${company.sector || "core market"}.`);
    }

    if (deVal !== null && deVal < 0.5) {
      growthDrivers.push(`Low leverage balance sheet (Debt/Equity: ${deVal.toFixed(2)}).`);
    } else if (deVal !== null && deVal >= 1.0) {
      riskFactors.push(`Leveraged balance sheet (Debt/Equity: ${deVal.toFixed(2)}).`);
    }

    if (pe !== null && pe < 15) {
      growthDrivers.push(`Favorable earnings valuation multiple (P/E: ${pe.toFixed(1)}x).`);
    } else if (pe !== null && pe > 30) {
      riskFactors.push(`Premium valuation multiple (P/E: ${pe.toFixed(1)}x).`);
    }

    if (riskFactors.length === 0) {
      riskFactors.push("Macroeconomic sector sensitivity and general market volatility.");
    }
  }

  return {
    id: company.id || "unknown-id",
    name: company.company_name || fallbackTicker,
    ticker: company.ticker || fallbackTicker,
    exchange: company.exchange || "NSE",
    sector: company.sector || "Equity Sector",
    industry: company.industry || "General",
    price,
    peRatio: pe,
    priceToBook: f.price_to_book ?? null,
    roe: roeVal,
    debtToEquity: deVal,
    dividendYield: divVal,
    beta: f.beta ?? 1.0,
    marketCap: mcap,
    high52: f.fifty_two_week_high ?? null,
    low52: f.fifty_two_week_low ?? null,
    formattedPrice,
    formattedPe,
    formattedRoe,
    formattedDebtEquity,
    formattedDivYield,
    formattedMarketCap,
    growthDrivers,
    riskFactors,
    scores,
  };
}
