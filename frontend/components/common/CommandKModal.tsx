"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  TrendingUp,
  Bot,
  BookOpen,
  BarChart3,
  X,
  ArrowRight,
  Building2,
  Loader2,
} from "lucide-react";
import { CompanyService, Company } from "@/services/api";

interface CommandKModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandKModal({ isOpen, onClose }: CommandKModalProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Company[]>([]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await CompanyService.list({ search: query, limit: 5 });
        if (res && res.companies) {
          setSearchResults(res.companies);
        }
      } catch (err) {
        console.warn("Company search query error:", err);
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  const navigateTo = (path: string) => {
    router.push(path);
    onClose();
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/markets?ticker=${encodeURIComponent(query)}`);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl rounded-3xl glass-panel border border-white/15 p-6 shadow-2xl flex flex-col gap-6 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/10"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Form Search Input */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-3 border-b border-white/10 pb-4">
          <Search className="h-5 w-5 text-blue-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search backend company (e.g. RELIANCE, TCS, HDFC)..."
            autoFocus
            className="w-full bg-transparent text-lg text-white placeholder-slate-500 focus:outline-none"
          />
          {loading && <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />}
        </form>

        {/* Live Search Results */}
        {searchResults.length > 0 && (
          <div className="flex flex-col gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-2">
              Database Matches ({searchResults.length})
            </span>
            <div className="space-y-1">
              {searchResults.map((c) => (
                <button
                  key={c.id}
                  onClick={() => navigateTo(`/markets?ticker=${c.ticker}`)}
                  className="w-full flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-blue-600/20 border border-white/5 text-left transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Building2 className="h-4 w-4 text-blue-400" />
                    <div className="flex flex-col">
                      <span className="font-semibold text-sm text-white">{c.company_name}</span>
                      <span className="text-xs text-slate-400">{c.ticker} • {c.exchange}</span>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-500" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions Shortcuts */}
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-2">
            Quick Actions
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              onClick={() => navigateTo("/research")}
              className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-blue-600/20 hover:border-blue-500/30 border border-white/5 text-left text-sm font-medium text-slate-200 hover:text-white transition-all group"
            >
              <div className="flex items-center gap-3">
                <Bot className="h-4 w-4 text-blue-400" />
                <span>Ask AI Research Assistant</span>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
            </button>

            <button
              onClick={() => navigateTo("/markets")}
              className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-blue-600/20 hover:border-blue-500/30 border border-white/5 text-left text-sm font-medium text-slate-200 hover:text-white transition-all group"
            >
              <div className="flex items-center gap-3">
                <TrendingUp className="h-4 w-4 text-emerald-400" />
                <span>Open Market Analysis</span>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-1 transition-all" />
            </button>

            <button
              onClick={() => navigateTo("/insights")}
              className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-blue-600/20 hover:border-blue-500/30 border border-white/5 text-left text-sm font-medium text-slate-200 hover:text-white transition-all group"
            >
              <div className="flex items-center gap-3">
                <BarChart3 className="h-4 w-4 text-purple-400" />
                <span>Open Insights Dashboard</span>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-purple-400 group-hover:translate-x-1 transition-all" />
            </button>

            <button
              onClick={() => navigateTo("/knowledge-hub")}
              className="flex items-center justify-between p-3 rounded-2xl bg-white/5 hover:bg-blue-600/20 hover:border-blue-500/30 border border-white/5 text-left text-sm font-medium text-slate-200 hover:text-white transition-all group"
            >
              <div className="flex items-center gap-3">
                <BookOpen className="h-4 w-4 text-amber-400" />
                <span>Search Knowledge Hub</span>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-amber-400 group-hover:translate-x-1 transition-all" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
