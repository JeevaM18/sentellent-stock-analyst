"use client";

import React from "react";
import {
  BarChart3,
  PieChart as PieChartIcon,
  TrendingUp,
  Globe,
  Layers,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";

const SECTOR_DATA = [
  { name: "IT & Software", value: 35, color: "#4F8CFF" },
  { name: "Banking & Finance", value: 25, color: "#8B5CF6" },
  { name: "Energy & Petrochem", value: 20, color: "#10B981" },
  { name: "Automobile", value: 12, color: "#F59E0B" },
  { name: "FMCG & Consumer", value: 8, color: "#EF4444" },
];

const SENTIMENT_TIMELINE = [
  { day: "Mon", Bullish: 65, Bearish: 15 },
  { day: "Tue", Bullish: 70, Bearish: 12 },
  { day: "Wed", Bullish: 68, Bearish: 18 },
  { day: "Thu", Bullish: 75, Bearish: 10 },
  { day: "Fri", Bullish: 82, Bearish: 8 },
];

const NEWS_SOURCES = [
  { name: "Economic Times", count: 42 },
  { name: "Reuters", count: 35 },
  { name: "Bloomberg", count: 28 },
  { name: "CNBC TV18", count: 22 },
];

export default function InsightsPage() {
  return (
    <div className="flex flex-col gap-8 max-w-7xl mx-auto animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex items-center justify-between p-6 rounded-3xl glass-panel border border-white/10 shadow-2xl">
        <div className="flex items-center gap-3">
          <BarChart3 className="h-6 w-6 text-purple-400" />
          <div>
            <h1 className="font-extrabold text-2xl text-white">Insights Center</h1>
            <p className="text-xs text-slate-400">PowerBI-style visual analytics across sectors, news sources, sentiment timeline, and market heatmap</p>
          </div>
        </div>
      </div>

      {/* Bento Grid Analytics Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Chart 1: Sector Distribution Donut Chart */}
        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <PieChartIcon className="h-4 w-4 text-blue-400" /> Sector Distribution
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={SECTOR_DATA} innerRadius={60} outerRadius={85} paddingAngle={4} dataKey="value">
                  {SECTOR_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "#0D1225", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 text-xs">
            {SECTOR_DATA.map((s) => (
              <div key={s.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                  <span className="text-slate-300">{s.name}</span>
                </div>
                <span className="font-bold text-white">{s.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Chart 2: Sentiment Timeline Line Chart */}
        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-emerald-400" /> Sentiment Timeline
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={SENTIMENT_TIMELINE}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" stroke="#94A3B8" fontSize={12} />
                <YAxis stroke="#94A3B8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: "#0D1225", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px" }} />
                <Line type="monotone" dataKey="Bullish" stroke="#10B981" strokeWidth={3} />
                <Line type="monotone" dataKey="Bearish" stroke="#EF4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-around text-xs pt-2 border-t border-white/5">
            <span className="text-emerald-400 font-semibold">● Bullish Trend (82%)</span>
            <span className="text-rose-400 font-semibold">● Bearish Pressure (8%)</span>
          </div>
        </div>

        {/* Chart 3: News Sources Bar Chart */}
        <div className="rounded-3xl glass-panel p-6 border border-white/10 flex flex-col gap-4 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Globe className="h-4 w-4 text-purple-400" /> Ingested News Coverage
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={NEWS_SOURCES} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#94A3B8" fontSize={12} />
                <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={10} width={90} />
                <Tooltip contentStyle={{ backgroundColor: "#0D1225", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px" }} />
                <Bar dataKey="count" fill="#8B5CF6" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <span className="text-[11px] text-slate-400 text-center">127 Total Ingested Articles</span>
        </div>
      </div>
    </div>
  );
}
