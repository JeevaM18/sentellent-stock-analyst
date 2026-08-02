"use client";

import React from "react";
import { AlertTriangle, RefreshCw, Server, Database, Sparkles, Wifi } from "lucide-react";

interface ErrorCardProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export function ErrorCard({
  title = "Unable to connect to Sentellent AI",
  message,
  onRetry,
}: ErrorCardProps) {
  return (
    <div className="p-6 rounded-3xl glass-panel border border-rose-500/20 bg-rose-950/10 flex flex-col gap-4 max-w-xl mx-auto shadow-2xl animate-in fade-in duration-200">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
          <AlertTriangle className="h-5 w-5" />
        </div>
        <div className="flex flex-col">
          <h3 className="font-extrabold text-base text-white">{title}</h3>
          {message && <p className="text-xs text-rose-300/80 mt-0.5">{message}</p>}
        </div>
      </div>

      <div className="p-3.5 rounded-2xl bg-black/20 border border-white/5 space-y-2 text-xs text-slate-300">
        <span className="font-semibold text-slate-200">Please verify backend health:</span>
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Server className="h-3.5 w-3.5 text-emerald-400" />
            <span>FastAPI Server (Port 8000)</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Database className="h-3.5 w-3.5 text-purple-400" />
            <span>PostgreSQL pgvector</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Sparkles className="h-3.5 w-3.5 text-sky-400" />
            <span>Gemini API Key</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <Wifi className="h-3.5 w-3.5 text-blue-400" />
            <span>CORS Headers</span>
          </div>
        </div>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="w-full py-2.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 font-semibold text-xs border border-rose-500/30 flex items-center justify-center gap-2 transition-all shadow-md"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
}
