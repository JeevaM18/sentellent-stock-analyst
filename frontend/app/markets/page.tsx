"use client";

import React, { useState, useEffect } from "react";
import {
  BarChart2,
  Sparkles,
  ShieldCheck,
  Building2,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Loader2,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";
import {
  CompanyService,
  RecommendationService,
  Company,
  RecommendationItem,
  CompanyNewsItem,
} from "@/services/api";
import { mapCompany, MappedCompany } from "@/services/companyMapper";
import { ErrorCard } from "@/components/common/ErrorCard";
import { SkeletonCard } from "@/components/common/Skeleton";

// Helper to generate dynamic historical price candles for a specific stock
function generateTickerChartData(ticker: string, price: number, low?: number | null, high?: number | null) {
  const basePrice = price || 1000;
  const minP = low || basePrice * 0.85;
  const maxP = high || basePrice * 1.15;

  // Deterministic seed variance based on ticker characters
  const hash = ticker.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"];

  return months.map((m, idx) => {
    const factor = Math.sin(hash + idx * 1.5) * 0.12;
    const currentP = Math.min(maxP, Math.max(minP, basePrice * (0.9 + factor + idx * 0.02)));
    const vol = Math.floor(1000 + ((hash * (idx + 1)) % 3000));
    return {
      date: m,
      price: Number(currentP.toFixed(2)),
      volume: vol,
    };
  });
}

export default function MarketsPage() {
  const [selectedTicker, setSelectedTicker] = useState("RELIANCE");
  const [chartType, setChartType] = useState<"area" | "bar">("area");
  const [loading, setLoading] = useState(true);
  const [company, setCompany] = useState<Company | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationItem | null>(null);
  const [news, setNews] = useState<CompanyNewsItem[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadStockData() {
      setLoading(true);
      setErrorMsg(null);
      setCompany(null);
      setRecommendation(null);
      setNews([]);

      try {
        // 1. Fetch Company Details & Fundamentals (No LLM)
        const comp = await CompanyService.getByTicker(selectedTicker);
        if (isMounted) setCompany(comp);
      } catch (err: unknown) {
        console.warn(`Error loading company data for ${selectedTicker}:`, err);
        if (isMounted) setErrorMsg(`Failed to load company details for ${selectedTicker}`);
      }

      try {
        // 2. Fetch Deterministic Recommendation Signals (No LLM)
        const recRes = await RecommendationService.get(10);
        if (recRes && recRes.recommendations && isMounted) {
          const match = recRes.recommendations.find(
            (r) => r.ticker.toUpperCase() === selectedTicker.toUpperCase()
          );
          if (match) {
            setRecommendation(match);
          }
        }
      } catch (err: unknown) {
        console.warn(`Error loading recommendations for ${selectedTicker}:`, err);
      }

      try {
        // 3. Fetch Ticker-Specific News via Direct PostgreSQL SQL (No Vector Search, No LLM)
        const newsRes = await CompanyService.getNews(selectedTicker, 3);
        if (newsRes && isMounted) {
          setNews(newsRes);
        }
      } catch (err: unknown) {
        console.warn(`Error loading news for ${selectedTicker}:`, err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadStockData();
    return () => {
      isMounted = false;
    };
  }, [selectedTicker]);

  // Clean Mapped Company Data
  const mappedComp: MappedCompany = mapCompany(company, selectedTicker);

  const chartData = generateTickerChartData(selectedTicker, mappedComp.price, mappedComp.low52, mappedComp.high52);
  const startPrice = chartData[0]?.price || 1;
  const endPrice = chartData[chartData.length - 1]?.price || 1;
  const priceChangePercent = (((endPrice - startPrice) / startPrice) * 100).toFixed(1);
  const isPositive = Number(priceChangePercent) >= 0;

  // Stock Specific Score Calculation
  const overallScore = recommendation?.overall_score ?? mappedComp.scores.overallScore;
  const confidenceScore = recommendation?.confidence ?? mappedComp.scores.confidence;
  const fundamentalScore = recommendation?.fundamental_score ?? mappedComp.scores.fundamentalScore;
  const newsScore = recommendation?.news_score ?? mappedComp.scores.newsScore;
  const memoryScore = recommendation?.memory_score ?? mappedComp.scores.memoryScore;
  const ratingText = mappedComp.scores.rating;

  return (
    <div className="flex flex-col gap-6 max-w-[1600px] mx-auto animate-in fade-in duration-300">
      {/* Ticker Selector Bar */}
      <div className="flex items-center justify-between gap-4 p-4 rounded-2xl glass-panel border border-white/10 shadow-2xl">
        <div className="flex items-center gap-3">
          <Building2 className="h-5 w-5 text-blue-400" />
          <span className="font-bold text-lg text-white">Market Screener &amp; Stock Intelligence</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "ITC", "COALINDIA", "NTPC"].map((t) => (
            <button
              key={t}
              onClick={() => setSelectedTicker(t)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                selectedTicker === t
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20 border border-blue-400/30"
                  : "bg-white/5 hover:bg-white/10 text-slate-300 border border-white/5"
              }`}
            >
              <span>{t}</span>
              {selectedTicker === t && loading && <Loader2 className="h-3 w-3 animate-spin text-white" />}
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <ErrorCard title="Stock Data Sync Error" message={errorMsg} onRetry={() => setSelectedTicker(selectedTicker)} />
      )}

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7">
            <SkeletonCard />
          </div>
          <div className="lg:col-span-5 space-y-4">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      ) : (
        /* Bloomberg-Style Split Workspace */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Panel: TradingView-Style Interactive Recharts (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-6 shadow-2xl">
              {/* Chart Control Header */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="h-11 w-11 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center font-extrabold text-sm text-blue-400">
                    {selectedTicker.slice(0, 3)}
                  </div>
                  <div className="flex flex-col">
                    <span className="font-extrabold text-xl text-white">{mappedComp.name}</span>
                    <span className="text-xs text-slate-400">
                      NSE: {mappedComp.ticker} • {mappedComp.sector} • {mappedComp.exchange}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setChartType("area")}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold ${chartType === "area" ? "bg-blue-600 text-white shadow-md shadow-blue-500/20" : "bg-white/5 text-slate-400"}`}
                  >
                    Price Trend
                  </button>
                  <button
                    onClick={() => setChartType("bar")}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold ${chartType === "bar" ? "bg-blue-600 text-white shadow-md shadow-blue-500/20" : "bg-white/5 text-slate-400"}`}
                  >
                    Volume
                  </button>
                </div>
              </div>

              {/* Price Header Stats */}
              <div className="flex items-baseline gap-4">
                <span className="text-3xl md:text-4xl font-extrabold text-white">
                  {mappedComp.formattedPrice}
                </span>
                <span
                  className={`text-xs md:text-sm font-bold px-2.5 py-1 rounded-xl border flex items-center gap-1 ${
                    isPositive
                      ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                      : "text-rose-400 bg-rose-500/10 border-rose-500/20"
                  }`}
                >
                  {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                  {isPositive ? `+${priceChangePercent}%` : `${priceChangePercent}%`} Trend
                </span>
              </div>

              {/* Main Interactive Recharts */}
              <div className="h-80 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  {chartType === "area" ? (
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#4F8CFF" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#4F8CFF" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" stroke="#94A3B8" fontSize={12} />
                      <YAxis stroke="#94A3B8" fontSize={12} domain={["auto", "auto"]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0D1225", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px" }}
                        itemStyle={{ color: "#4F8CFF" }}
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        formatter={(val: any) => [`₹${val}`, "Price"]}
                      />
                      <Area type="monotone" dataKey="price" stroke="#4F8CFF" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
                    </AreaChart>
                  ) : (
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="date" stroke="#94A3B8" fontSize={12} />
                      <YAxis stroke="#94A3B8" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: "#0D1225", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px" }} />
                      <Bar dataKey="volume" fill="#8B5CF6" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </div>

              {/* Ticker-Specific Direct PostgreSQL News */}
              {news.length > 0 && (
                <div className="border-t border-white/10 pt-4 space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-amber-400" /> Recent News ({selectedTicker})
                  </span>
                  <div className="grid grid-cols-1 gap-2">
                    {news.map((item, idx) => (
                      <div key={idx} className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-white truncate max-w-[300px]">{item.title}</span>
                          <span className="text-[11px] font-bold text-emerald-400">{item.sentiment}</span>
                        </div>
                        <p className="text-[11px] text-slate-300 line-clamp-2">{item.summary}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Scrollable Panel: Dynamic AI Signals & Screener Ratios (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-6 space-y-4">
            {/* AI Deterministic Recommendation Badge Card */}
            <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 bg-gradient-to-br from-blue-900/20 to-indigo-900/20 shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-400">
                  <Sparkles className="h-4 w-4" /> AI Deterministic Signal
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold">
                  {ratingText}
                </span>
              </div>

              <div className="flex items-center justify-between my-1">
                <div className="flex flex-col">
                  <span className="text-3xl font-extrabold text-white">{overallScore.toFixed(1)} / 100</span>
                  <span className="text-xs text-slate-400">Weighted Score ({selectedTicker})</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-sm font-bold text-emerald-400">High Confidence</span>
                  <span className="text-xs text-slate-400">Empirical Score {(confidenceScore * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-slate-400">Fundamentals</div>
                  <div className="font-bold text-white mt-0.5">{fundamentalScore.toFixed(0)} / 100</div>
                </div>
                <div className="p-2.5 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-slate-400">News Sentiment</div>
                  <div className="font-bold text-white mt-0.5">{newsScore.toFixed(0)} / 100</div>
                </div>
                <div className="p-2.5 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-slate-400">Memory Match</div>
                  <div className="font-bold text-white mt-0.5">{memoryScore.toFixed(0)} / 100</div>
                </div>
              </div>
            </div>

            {/* AI Executive Summary Card (Deterministic Rule-Based) */}
            <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-2xl">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-purple-400" /> Executive Financial Summary ({selectedTicker})
              </span>

              <div className="space-y-3 text-xs leading-relaxed text-slate-300">
                <div className="p-3.5 rounded-2xl bg-white/5 border border-white/5 flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 min-w-4 mt-0.5" />
                  <div>
                    <strong className="text-white">Growth Drivers:</strong>{" "}
                    {mappedComp.growthDrivers[0] || `Strong operational momentum in ${mappedComp.sector}.`}
                  </div>
                </div>

                <div className="p-3.5 rounded-2xl bg-white/5 border border-white/5 flex items-start gap-3">
                  <AlertTriangle className="h-4 w-4 text-amber-400 min-w-4 mt-0.5" />
                  <div>
                    <strong className="text-white">Risk Analysis:</strong>{" "}
                    {mappedComp.riskFactors[0] || `Sector competition and rate fluctuations.`}
                  </div>
                </div>
              </div>
            </div>

            {/* Screener Fundamentals Grid */}
            <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-2xl">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <BarChart2 className="h-4 w-4 text-emerald-400" /> Screener Financial Ratios
              </span>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">P/E Ratio</span>
                  <span className="text-sm font-bold text-white mt-0.5">{mappedComp.formattedPe}</span>
                </div>
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">Debt to Equity</span>
                  <span className="text-sm font-bold text-emerald-400 mt-0.5">{mappedComp.formattedDebtEquity}</span>
                </div>
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">ROE</span>
                  <span className="text-sm font-bold text-white mt-0.5">{mappedComp.formattedRoe}</span>
                </div>
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">Dividend Yield</span>
                  <span className="text-sm font-bold text-white mt-0.5">{mappedComp.formattedDivYield}</span>
                </div>
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">Beta</span>
                  <span className="text-sm font-bold text-white mt-0.5">{mappedComp.beta ?? "1.00"}</span>
                </div>
                <div className="p-3 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
                  <span className="text-[11px] text-slate-400 font-medium">Market Cap</span>
                  <span className="text-sm font-bold text-white mt-0.5">{mappedComp.formattedMarketCap}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
