"use client";

import React from "react";
import { Sparkles, ShieldCheck, BarChart2, Bot, BookOpen, ArrowRight, Zap, Database } from "lucide-react";
import { useAuth } from "./AuthProvider";

export default function PublicLandingPage() {
  const { login } = useAuth();

  return (
    <div className="flex flex-col gap-12 max-w-6xl mx-auto py-12 px-6 animate-in fade-in duration-500">
      {/* Hero Banner */}
      <div className="rounded-3xl glass-panel p-8 md:p-12 border border-white/10 flex flex-col items-center text-center gap-8 bg-gradient-to-br from-blue-950/40 via-slate-900/60 to-purple-950/40 shadow-2xl relative overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-24 h-72 w-72 rounded-full bg-purple-500/10 blur-3xl" />

        {/* Telemetry Badge */}
        <div className="flex flex-wrap items-center justify-center gap-3 text-xs font-mono bg-white/5 border border-white/10 px-4 py-2 rounded-full text-slate-300">
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" /> AI Services Online 232ms
          </span>
          <span className="text-slate-500">•</span>
          <span className="flex items-center gap-1.5 text-blue-400">
            <Database className="h-3.5 w-3.5" /> PostgreSQL Connected
          </span>
          <span className="text-slate-500">•</span>
          <span className="text-amber-400">1,256 Companies Tracked</span>
        </div>

        <div className="flex flex-col gap-4 max-w-3xl">
          <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight">
            Sentellent Alpha
          </h1>
          <p className="text-lg md:text-xl font-medium text-slate-300">
            AI-Powered Market Intelligence Platform
          </p>
          <p className="text-xs md:text-sm text-slate-400 leading-relaxed max-w-2xl mx-auto">
            Institutional-grade multi-agent financial analytics, deterministic ratio scoring models, vector news retrieval, and personalized portfolio intelligence.
          </p>
        </div>

        {/* Call to Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={login}
            className="px-8 py-4 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-extrabold text-sm shadow-xl shadow-blue-500/25 flex items-center gap-3 transition-all transform hover:-translate-y-0.5"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google</span>
          </button>
        </div>
      </div>

      {/* Flagship Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col justify-between gap-4 shadow-xl glass-panel-hover">
          <div className="h-12 w-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <BarChart2 className="h-6 w-6" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="font-extrabold text-white text-base">Market Screener</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Deterministic valuation modeling, financial ratio analysis, and live yFinance ticker integration.
            </p>
          </div>
          <div className="flex items-center text-xs font-bold text-blue-400 gap-1 pt-2">
            <span>Deterministic Ratios</span> <ArrowRight className="h-3.5 w-3.5" />
          </div>
        </div>

        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col justify-between gap-4 shadow-xl glass-panel-hover">
          <div className="h-12 w-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Bot className="h-6 w-6" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="font-extrabold text-white text-base">LangGraph RAG Agent</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Multi-agent conversational analyst with OpenRouter fallback and real-time news citations.
            </p>
          </div>
          <div className="flex items-center text-xs font-bold text-purple-400 gap-1 pt-2">
            <span>Multi-Model AI</span> <ArrowRight className="h-3.5 w-3.5" />
          </div>
        </div>

        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col justify-between gap-4 shadow-xl glass-panel-hover">
          <div className="h-12 w-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Sparkles className="h-6 w-6" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="font-extrabold text-white text-base">Portfolio Workspace</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Personalized watchlists, investor memory profiles, and tailor-made AI stock recommendations.
            </p>
          </div>
          <div className="flex items-center text-xs font-bold text-amber-400 gap-1 pt-2">
            <span>Per-User Memory</span> <ArrowRight className="h-3.5 w-3.5" />
          </div>
        </div>

        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col justify-between gap-4 shadow-xl glass-panel-hover">
          <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <BookOpen className="h-6 w-6" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="font-extrabold text-white text-base">Knowledge Hub</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              pgvector similarity search across 42,000+ financial news chunks with source attribution.
            </p>
          </div>
          <div className="flex items-center text-xs font-bold text-emerald-400 gap-1 pt-2">
            <span>Vector Search</span> <ArrowRight className="h-3.5 w-3.5" />
          </div>
        </div>
      </div>
    </div>
  );
}
