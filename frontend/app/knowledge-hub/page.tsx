"use client";

import React, { useState } from "react";
import {
  BookOpen,
  Search,
  FileText,
  Database,
  ExternalLink,
  Plus,
  Inbox,
  Loader2,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  X,
} from "lucide-react";
import { RetrievalService, RetrievalChunk, NewsService } from "@/services/api";
import { ErrorCard } from "@/components/common/ErrorCard";

const POPULAR_TICKERS = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "ITC", "SBIN", "ICICIBANK"];

export default function KnowledgeHubPage() {
  const [query, setQuery] = useState("RELIANCE earnings quarterly report");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Ingestion Modal State
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [ingestTicker, setIngestTicker] = useState("RELIANCE");
  const [ingesting, setIngesting] = useState(false);
  const [ingestSuccessMsg, setIngestSuccessMsg] = useState<string | null>(null);

  const [chunks, setChunks] = useState<RetrievalChunk[]>([
    {
      chunk_id: "c-1",
      document_id: "doc-1",
      ticker: "RELIANCE",
      company_name: "Reliance Industries",
      similarity: 0.92,
      content: "Reliance Industries reported a 12% year-on-year increase in quarterly net profit, driven by strong growth in its digital and retail divisions...",
      chunk_index: 0,
      source_title: "Reliance Q1 Financial Report 2026",
      source_url: "https://screener.in/company/RELIANCE/",
    },
    {
      chunk_id: "c-2",
      document_id: "doc-2",
      ticker: "TCS",
      company_name: "Tata Consultancy Services",
      similarity: 0.86,
      content: "TCS announced a multi-year digital transformation contract worth $1.2B with European financial institutions...",
      chunk_index: 1,
      source_title: "TCS Tech Expansion Brief 2026",
      source_url: "https://screener.in/company/TCS/",
    },
  ]);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await RetrievalService.search(query, 6);
      if (res && res.chunks && res.chunks.length > 0) {
        setChunks(res.chunks);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to search vector knowledge store.";
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const tickerClean = ingestTicker.trim().toUpperCase();
    if (!tickerClean || ingesting) return;

    setIngesting(true);
    setIngestSuccessMsg(null);

    try {
      const res = await NewsService.ingest(tickerClean);
      if (res && res.success) {
        setIngestSuccessMsg(res.message || `Successfully ingested data for ${tickerClean}!`);
        // Refresh search results automatically
        setQuery(`${tickerClean} financial earnings news`);
        setTimeout(() => {
          handleSearch();
        }, 500);
      }
    } catch (err) {
      console.error("Ingestion error:", err);
      setIngestSuccessMsg(`Error ingesting data for ${tickerClean}. Please try again.`);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-7xl mx-auto animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between p-6 rounded-3xl glass-panel border border-white/10 shadow-2xl gap-4">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-extrabold text-2xl text-white">Knowledge Hub (RAG Inspector)</h1>
            <p className="text-xs text-slate-400">Search ingested financial SEC filings, Screener reports, and RSS news stored in PostgreSQL pgvector</p>
          </div>
        </div>

        <button
          onClick={() => {
            setIngestSuccessMsg(null);
            setShowIngestModal(true);
          }}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
        >
          <Plus className="h-4 w-4" />
          <span>Ingest New Ticker</span>
        </button>
      </div>

      {/* Vector Knowledge Search Bar */}
      <form onSubmit={handleSearch} className="flex items-center gap-3 bg-white/5 border border-white/15 rounded-2xl p-2 shadow-2xl backdrop-blur-xl focus-within:border-amber-500/50 transition-all">
        <Search className="h-5 w-5 text-amber-400 ml-3" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search vector knowledge store (e.g. RELIANCE profit, TCS revenue, banking dividends)..."
          className="w-full bg-transparent text-sm md:text-base text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 text-white font-semibold text-xs md:text-sm flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Searching pgvector...</span>
            </>
          ) : (
            <span>Vector Search</span>
          )}
        </button>
      </form>

      {/* Error state */}
      {errorMsg && <ErrorCard title="Search Error" message={errorMsg} />}

      {/* Retrieval Chunks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {chunks.map((chunk) => (
          <div
            key={chunk.chunk_id}
            className="p-6 rounded-3xl glass-panel border border-white/10 flex flex-col justify-between gap-4 shadow-xl hover:border-amber-500/30 transition-all group"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-amber-400" />
                <span className="font-bold text-base text-white group-hover:text-amber-300 transition-colors">
                  {chunk.source_title || `${chunk.ticker} Vector Chunk`}
                </span>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">
                {(chunk.similarity * 100).toFixed(1)}% Similarity
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-mono bg-black/30 p-4 rounded-2xl border border-white/5 italic">
              "{chunk.content}"
            </p>

            <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-white/5">
              <span className="flex items-center gap-1 font-mono text-[11px]">
                <Database className="h-3.5 w-3.5 text-blue-400" /> Chunk #{chunk.chunk_index}
              </span>
              {chunk.source_url && (
                <a
                  href={chunk.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1"
                >
                  Source Link <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {chunks.length === 0 && !loading && (
        <div className="p-16 rounded-3xl glass-panel border border-white/10 flex flex-col items-center justify-center gap-3 text-slate-400 text-center">
          <Inbox className="h-12 w-12 text-slate-500" />
          <span className="font-semibold text-slate-200">No vector chunks found for your query.</span>
          <p className="text-xs text-slate-400 max-w-sm">
            Try ingesting news for a new ticker using the "+ Ingest New Ticker" button above!
          </p>
        </div>
      )}

      {/* Ingest New Ticker Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <form
            onSubmit={handleIngestSubmit}
            className="w-full max-w-md rounded-3xl glass-panel p-6 border border-slate-700/80 bg-[#090d1a] flex flex-col gap-6 shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <span className="font-bold text-sm text-white flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-400" /> Ingest Financial Data &amp; News
              </span>
              <button
                type="button"
                onClick={() => setShowIngestModal(false)}
                className="text-slate-400 hover:text-white text-xs cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Fetches live Google News RSS, Screener filings, &amp; generates vector embeddings stored directly in PostgreSQL pgvector.
            </p>

            {/* Quick Selection Chips */}
            <div className="flex flex-col gap-2">
              <span className="text-[11px] text-slate-400 font-semibold">Quick Select Marquee Ticker:</span>
              <div className="flex flex-wrap gap-1.5">
                {POPULAR_TICKERS.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setIngestTicker(t)}
                    className={`px-2.5 py-1 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                      ingestTicker === t
                        ? "bg-blue-600 text-white border-blue-400"
                        : "bg-white/5 text-slate-300 border-white/10 hover:bg-white/10"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Ticker Input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-300">Ticker Symbol</label>
              <input
                type="text"
                value={ingestTicker}
                onChange={(e) => setIngestTicker(e.target.value.toUpperCase())}
                placeholder="Enter ticker (e.g. RELIANCE, TCS, INFY)"
                className="bg-white/5 border border-white/15 rounded-xl px-3.5 py-2.5 text-xs text-white uppercase focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            {/* Success Message Banner */}
            {ingestSuccessMsg && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>{ingestSuccessMsg}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowIngestModal(false)}
                className="px-4 py-2 rounded-xl bg-white/5 text-slate-400 text-xs font-semibold hover:text-white"
              >
                Close
              </button>
              <button
                type="submit"
                disabled={ingesting}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/20 cursor-pointer"
              >
                {ingesting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Ingesting to pgvector...</span>
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    <span>Start Ingestion</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
