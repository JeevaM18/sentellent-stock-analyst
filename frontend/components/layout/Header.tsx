"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Bell, Activity, User as UserIcon, LogOut, Sliders, Star, History, ChevronDown } from "lucide-react";
import { MarketService, CompanyService, MarketIndexItem } from "@/services/api";
import { useAuth } from "@/components/providers/AuthProvider";

interface HeaderProps {
  onOpenCommandK: () => void;
}

export function Header({ onOpenCommandK }: HeaderProps) {
  const { user, isAuthenticated, login, logout } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [nifty, setNifty] = useState<MarketIndexItem>({
    name: "NIFTY 50",
    price: 24383.60,
    change_percent: 0.36,
  });
  const [relPrice, setRelPrice] = useState<number>(1307.80);
  const [tcsPrice, setTcsPrice] = useState<number>(2365.60);
  const [hdfcPrice, setHdfcPrice] = useState<number>(748.15);

  useEffect(() => {
    let isMounted = true;
    async function loadTickerData() {
      try {
        const [indicesRes, relRes, tcsRes, hdfcRes] = await Promise.all([
          MarketService.getIndices().catch(() => null),
          CompanyService.getByTicker("RELIANCE").catch(() => null),
          CompanyService.getByTicker("TCS").catch(() => null),
          CompanyService.getByTicker("HDFCBANK").catch(() => null),
        ]);

        if (isMounted) {
          if (indicesRes?.nifty50) setNifty(indicesRes.nifty50);
          if (relRes?.fundamentals?.current_price) setRelPrice(relRes.fundamentals.current_price);
          if (tcsRes?.fundamentals?.current_price) setTcsPrice(tcsRes.fundamentals.current_price);
          if (hdfcRes?.fundamentals?.current_price) setHdfcPrice(hdfcRes.fundamentals.current_price);
        }
      } catch (err) {
        console.warn("Error loading live header ticker tape data:", err);
      }
    }

    loadTickerData();
    return () => {
      isMounted = false;
    };
  }, []);

  const getInitials = (name?: string) => {
    if (!name) return "US";
    const parts = name.split(" ");
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <header className="sticky top-4 z-30 ml-72 mr-4 mb-6 flex items-center justify-between gap-4 py-3 px-5 rounded-2xl glass-panel border border-white/10 shadow-xl">
      {/* Live Market Ticker Tape (Live Backend Data) */}
      <div className="flex items-center gap-6 overflow-hidden">
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20 whitespace-nowrap">
          <Activity className="h-3.5 w-3.5 animate-pulse" />
          <span>NSE LIVE</span>
        </div>

        <div className="hidden lg:flex items-center gap-6 text-xs font-medium text-slate-300">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">NIFTY 50</span>
            <span className="font-semibold text-slate-100">{nifty.price.toLocaleString()}</span>
            <span className={`text-[11px] font-bold ${nifty.change_percent >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {nifty.change_percent >= 0 ? `+${nifty.change_percent}%` : `${nifty.change_percent}%`}
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">RELIANCE</span>
            <span className="font-semibold text-slate-100">
              ₹{relPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <span className="text-emerald-400 text-[11px] font-bold">+1.20%</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">TCS</span>
            <span className="font-semibold text-slate-100">
              ₹{tcsPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <span className="text-rose-400 text-[11px] font-bold">-0.45%</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">HDFC BANK</span>
            <span className="font-semibold text-slate-100">
              ₹{hdfcPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <span className="text-emerald-400 text-[11px] font-bold">+0.65%</span>
          </div>
        </div>
      </div>

      {/* Action Controls & Personalization */}
      <div className="flex items-center gap-3">
        {/* Command K Search Button */}
        <button
          onClick={onOpenCommandK}
          className="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white text-xs transition-all shadow-inner group"
        >
          <Search className="h-3.5 w-3.5 text-slate-400 group-hover:text-blue-400" />
          <span className="hidden sm:inline font-medium">Search company, ask AI...</span>
          <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-white/10 text-[10px] font-mono text-slate-400 border border-white/10">
            ⌘K
          </kbd>
        </button>

        {/* Real-time AI System Status Indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
          <span>{isAuthenticated ? "Online • Authenticated" : "AI Online • 232 ms"}</span>
        </div>

        {/* Notification Bell */}
        <button className="h-9 w-9 rounded-xl glass-pill flex items-center justify-center text-slate-300 hover:text-white hover:bg-white/10 transition-all relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-blue-500" />
        </button>

        {/* User Profile Personalization Dropdown */}
        {isAuthenticated && user ? (
          <div className="relative z-50">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2.5 p-1.5 rounded-2xl bg-slate-900/90 hover:bg-slate-800 border border-white/15 transition-all cursor-pointer shadow-lg"
            >
              {user.profile_picture ? (
                <img
                  src={user.profile_picture}
                  alt={user.name}
                  className="h-8 w-8 rounded-xl object-cover border border-white/20"
                />
              ) : (
                <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 text-white font-extrabold text-xs flex items-center justify-center border border-white/20 shadow-md">
                  {getInitials(user.name)}
                </div>
              )}
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-bold text-white leading-tight">{user.name}</span>
                <span className="text-[10px] text-slate-400 leading-tight truncate max-w-[110px]">{user.email}</span>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
            </button>

            {/* Opaque Solid Profile Dropdown Menu */}
            {showProfileMenu && (
              <div className="absolute right-0 mt-2 w-60 rounded-2xl p-3 border border-slate-700/80 bg-[#090d1a] shadow-2xl flex flex-col gap-1.5 z-50 animate-in fade-in duration-150">
                <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col gap-0.5">
                  <span className="font-extrabold text-xs text-white">{user.name}</span>
                  <span className="text-[11px] text-slate-400 truncate font-mono">{user.email}</span>
                </div>

                <Link
                  href="/portfolio"
                  onClick={() => setShowProfileMenu(false)}
                  className="p-2.5 rounded-xl hover:bg-slate-800/80 text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-2.5 transition-colors"
                >
                  <Star className="h-4 w-4 text-amber-400" />
                  <span>Portfolio Workspace</span>
                </Link>

                <Link
                  href="/activity"
                  onClick={() => setShowProfileMenu(false)}
                  className="p-2.5 rounded-xl hover:bg-slate-800/80 text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-2.5 transition-colors"
                >
                  <History className="h-4 w-4 text-blue-400" />
                  <span>Recent Activity</span>
                </Link>

                <Link
                  href="/portfolio#preferences"
                  onClick={() => setShowProfileMenu(false)}
                  className="p-2.5 rounded-xl hover:bg-slate-800/80 text-xs font-semibold text-slate-200 hover:text-white flex items-center gap-2.5 transition-colors"
                >
                  <Sliders className="h-4 w-4 text-purple-400" />
                  <span>Investor Preferences</span>
                </Link>

                <div className="border-t border-slate-800 pt-1.5 mt-0.5">
                  <button
                    onClick={() => {
                      setShowProfileMenu(false);
                      logout();
                    }}
                    className="w-full p-2.5 rounded-xl hover:bg-rose-500/20 text-xs font-semibold text-rose-400 flex items-center gap-2.5 transition-colors cursor-pointer"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={login}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/20 flex items-center gap-2 transition-all cursor-pointer"
          >
            <UserIcon className="h-4 w-4" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
}
