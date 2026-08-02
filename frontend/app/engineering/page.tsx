"use client";

import React from "react";
import { Cpu, Server, Database, Bot, Sparkles, Layers, ShieldCheck, ArrowDown } from "lucide-react";

export default function EngineeringPage() {
  const PIPELINE_NODES = [
    { title: "Next.js 15 Client", subtitle: "Obsidian UI & AppShell", icon: LayoutIcon, color: "text-blue-400" },
    { title: "FastAPI REST Server", subtitle: "Python 3.13 API Router", icon: Server, color: "text-emerald-400" },
    { title: "PostgreSQL & pgvector", subtitle: "SQLAlchemy ORM & Vector Store", icon: Database, color: "text-purple-400" },
    { title: "LangGraph Agent Engine", subtitle: "Multi-Tool Planner & ToolRegistry", icon: Bot, color: "text-amber-400" },
    { title: "Investor Memory Engine", subtitle: "Personalized Memory & MergeEngine", icon: Layers, color: "text-indigo-400" },
    { title: "Recommendation Engine", subtitle: "Weighted Scoring (35% Fund, 25% News)", icon: ShieldCheck, color: "text-rose-400" },
    { title: "Gemini LLM Provider", subtitle: "Grounded Natural Language Advice", icon: Sparkles, color: "text-sky-400" },
  ];

  return (
    <div className="flex flex-col gap-8 max-w-6xl mx-auto animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-6 rounded-3xl glass-panel border border-white/10 shadow-2xl">
        <div className="flex items-center gap-3">
          <Cpu className="h-6 w-6 text-emerald-400" />
          <div>
            <h1 className="font-extrabold text-2xl text-white">System Architecture &amp; Pipeline</h1>
            <p className="text-xs text-slate-400">Interactive engineering visualization of Sentellent Alpha&apos;s end-to-end stack</p>
          </div>
        </div>
      </div>

      {/* Interactive Visual Pipeline Flow */}
      <div className="rounded-3xl glass-panel p-8 border border-white/10 flex flex-col gap-6 shadow-2xl">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Production AI Pipeline Flow</h2>

        <div className="flex flex-col items-center gap-4 py-4">
          {PIPELINE_NODES.map((node, idx) => {
            const Icon = node.icon;
            return (
              <React.Fragment key={idx}>
                <div className="w-full max-w-lg p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between shadow-lg hover:border-blue-500/40 transition-all">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                      <Icon className={`h-5 w-5 ${node.color}`} />
                    </div>
                    <div className="flex flex-col">
                      <span className="font-bold text-sm text-white">{node.title}</span>
                      <span className="text-xs text-slate-400">{node.subtitle}</span>
                    </div>
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-400 bg-white/5 px-2.5 py-1 rounded-md">
                    Step 0{idx + 1}
                  </span>
                </div>
                {idx < PIPELINE_NODES.length - 1 && (
                  <ArrowDown className="h-4 w-4 text-blue-400 opacity-60 animate-bounce" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function LayoutIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="2" strokeWidth="2" />
      <path d="M9 3v18" strokeWidth="2" />
    </svg>
  );
}
