"use client";

import React, { useState } from "react";
import Link from "next/link";
import { History, Search, Bot, BarChart2, BookOpen, Clock, ArrowRight, ShieldCheck, User } from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";

interface ActivityItem {
  id: string;
  type: "view" | "search" | "chat" | "login";
  title: string;
  detail: string;
  timestamp: string;
  link: string;
}

export default function ActivityPage() {
  const { user } = useAuth();
  const [activities] = useState<ActivityItem[]>([
    {
      id: "1",
      type: "login",
      title: "Authenticated Login Session",
      detail: "Google OAuth token verified & PostgreSQL user synchronized",
      timestamp: "Today, 10:42 AM",
      link: "/",
    },
    {
      id: "2",
      type: "view",
      title: "Viewed Screener Ratios: TCS",
      detail: "Examined ROE 58.4%, P/E 30.5x, and Debt/Eq 0.08",
      timestamp: "Today, 10:35 AM",
      link: "/markets?ticker=TCS",
    },
    {
      id: "3",
      type: "chat",
      title: "Research AI Query: Reliance Revenue Growth",
      detail: "LangGraph agent retrieved 3 knowledge chunks with citations",
      timestamp: "Today, 10:15 AM",
      link: "/research?query=Reliance",
    },
    {
      id: "4",
      type: "search",
      title: "Knowledge Hub Search: RBI Repo Rate Impact",
      detail: "Vector search returned 5 news articles",
      timestamp: "Yesterday, 4:20 PM",
      link: "/knowledge-hub?query=RBI",
    },
    {
      id: "5",
      type: "view",
      title: "Viewed Portfolio & Watchlist Holdings",
      detail: "Updated Investor Memory preferences to Growth & Quality",
      timestamp: "Yesterday, 2:10 PM",
      link: "/portfolio",
    },
  ]);

  const getTypeIcon = (type: ActivityItem["type"]) => {
    switch (type) {
      case "login":
        return <User className="h-4 w-4 text-emerald-400" />;
      case "view":
        return <BarChart2 className="h-4 w-4 text-blue-400" />;
      case "chat":
        return <Bot className="h-4 w-4 text-purple-400" />;
      case "search":
        return <BookOpen className="h-4 w-4 text-amber-400" />;
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-6 rounded-3xl glass-panel border border-white/10 shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-bold">
            <History className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-extrabold text-2xl text-white">Recent Activity &amp; Audit Trail</h1>
            <p className="text-xs text-slate-400">
              Personalized search history, AI queries, and session activity for {user?.name || "Authenticated User"}
            </p>
          </div>
        </div>

        <span className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20 flex items-center gap-1.5">
          <ShieldCheck className="h-4 w-4" /> User Isolated
        </span>
      </div>

      {/* Activity Timeline */}
      <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-2xl">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Clock className="h-4 w-4 text-purple-400" /> Recent Search &amp; Research Audit History
        </span>

        <div className="space-y-3">
          {activities.map((act) => (
            <Link
              key={act.id}
              href={act.link}
              className="p-4 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-all group"
            >
              <div className="flex items-start gap-3.5">
                <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-0.5 sm:mt-0">
                  {getTypeIcon(act.type)}
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-sm text-white group-hover:text-blue-400 transition-colors">
                    {act.title}
                  </span>
                  <span className="text-xs text-slate-400">{act.detail}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                <span className="text-[11px] font-mono text-slate-400">{act.timestamp}</span>
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-white group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
