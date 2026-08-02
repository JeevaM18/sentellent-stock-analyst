"use client";

import React, { useState, useEffect } from "react";
import { Settings, Save, Sparkles, CheckCircle2, ShieldCheck } from "lucide-react";
import { api, InvestorMemory } from "@/services/api";

export default function PreferencesPage() {
  const [memory, setMemory] = useState<InvestorMemory>({
    risk_profile: "Moderate",
    investment_horizon: "Long Term",
    investment_style: "Growth",
    preferred_sectors: ["IT", "Banking"],
    avoided_sectors: ["Crypto"],
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function loadMemory() {
      try {
        const data = await api.getMemory();
        if (data) setMemory(data);
      } catch (err) {
        console.warn("Could not load investor memory:", err);
      }
    }
    loadMemory();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateMemory(memory);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.warn("Failed to update investor memory:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-6 rounded-3xl glass-panel border border-white/10 shadow-2xl">
        <div className="flex items-center gap-3">
          <Settings className="h-6 w-6 text-blue-400" />
          <div>
            <h1 className="font-extrabold text-2xl text-white">Investor Memory Preferences</h1>
            <p className="text-xs text-slate-400">Configure your personalized AI risk profile, investment style, and sector memory preferences</p>
          </div>
        </div>
      </div>

      {/* Editor Form */}
      <form onSubmit={handleSave} className="rounded-3xl glass-panel p-8 border border-white/10 flex flex-col gap-6 shadow-2xl space-y-2">
        {/* Risk Profile Selection */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Risk Profile</label>
          <div className="grid grid-cols-3 gap-3">
            {["Conservative", "Moderate", "Aggressive"].map((r) => (
              <button
                type="button"
                key={r}
                onClick={() => setMemory({ ...memory, risk_profile: r })}
                className={`py-3 rounded-2xl text-xs font-bold border transition-all ${
                  memory.risk_profile === r
                    ? "bg-blue-600 text-white border-blue-400 shadow-md shadow-blue-500/20"
                    : "bg-white/5 hover:bg-white/10 text-slate-300 border-white/5"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* Investment Horizon */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Investment Horizon</label>
          <div className="grid grid-cols-3 gap-3">
            {["Short Term", "Medium Term", "Long Term"].map((h) => (
              <button
                type="button"
                key={h}
                onClick={() => setMemory({ ...memory, investment_horizon: h })}
                className={`py-3 rounded-2xl text-xs font-bold border transition-all ${
                  memory.investment_horizon === h
                    ? "bg-blue-600 text-white border-blue-400 shadow-md shadow-blue-500/20"
                    : "bg-white/5 hover:bg-white/10 text-slate-300 border-white/5"
                }`}
              >
                {h}
              </button>
            ))}
          </div>
        </div>

        {/* Preferred Sectors */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Preferred Sectors (Comma Separated)</label>
          <input
            type="text"
            value={memory.preferred_sectors?.join(", ") || ""}
            onChange={(e) => setMemory({ ...memory, preferred_sectors: e.target.value.split(",").map((s) => s.trim()) })}
            placeholder="e.g. IT, Banking, Energy"
            className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* Avoided Sectors */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Avoided Sectors (Comma Separated)</label>
          <input
            type="text"
            value={memory.avoided_sectors?.join(", ") || ""}
            onChange={(e) => setMemory({ ...memory, avoided_sectors: e.target.value.split(",").map((s) => s.trim()) })}
            placeholder="e.g. Crypto, Penny Stocks"
            className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* Save Button */}
        <div className="flex items-center justify-between pt-4 border-t border-white/10">
          {saved ? (
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" /> Preferences saved to investor memory!
            </span>
          ) : (
            <span className="text-xs text-slate-400">Updates merge automatically into backend MemoryMergeEngine.</span>
          )}

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white font-semibold text-xs md:text-sm shadow-lg shadow-blue-500/25 flex items-center gap-2 transition-all"
          >
            <Save className="h-4 w-4" />
            <span>{saving ? "Saving..." : "Save Preferences"}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
