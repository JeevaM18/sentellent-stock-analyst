"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Bot,
  BarChart2,
  BookOpen,
  LineChart,
  History,
  Settings,
  TrendingUp,
  LogOut,
  User as UserIcon,
  Activity,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/providers/AuthProvider";

const MAIN_MENU = [
  { name: "Dashboard Overview", href: "/", icon: LayoutDashboard },
  { name: "Tracked Portfolio", href: "/portfolio", icon: Briefcase },
  { name: "RAG Chief Assistant", href: "/research", icon: Bot },
  { name: "Screener & Ratios", href: "/markets", icon: BarChart2 },
  { name: "Analytics & Visualizations", href: "/insights", icon: LineChart },
  { name: "Knowledge Hub", href: "/knowledge-hub", icon: BookOpen },
];

const SYSTEM_MENU = [
  { name: "Activity & History", href: "/activity", icon: History },
  { name: "Investor Preferences", href: "/preferences", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, isAuthenticated, login, logout } = useAuth();

  const getInitials = (name?: string) => {
    if (!name) return "US";
    const parts = name.split(" ");
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <aside className="fixed left-4 top-4 bottom-4 z-40 w-64 flex flex-col justify-between rounded-3xl glass-panel p-5 shadow-2xl border border-white/10 bg-[#070b19]/95 backdrop-blur-xl font-sans">
      <div className="flex flex-col gap-6">
        {/* Sleek Brand Logo Header */}
        <Link href="/" className="flex items-center gap-3 px-2 py-1 group">
          <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 flex items-center justify-center shadow-lg shadow-blue-600/30 border border-white/20 group-hover:scale-105 transition-transform">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="font-extrabold text-lg text-white tracking-tight flex items-center gap-1">
              Sentellent <span className="text-xs px-1.5 py-0.5 rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30 font-mono">ALPHA</span>
            </span>
            <span className="text-[11px] font-medium text-slate-400 tracking-wide">
              Market Intelligence
            </span>
          </div>
        </Link>

        {/* Main Navigation Section */}
        <div className="flex flex-col gap-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 px-3">
            MAIN MENU
          </span>

          <nav className="flex flex-col gap-1.5">
            {MAIN_MENU.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3.5 py-3 rounded-2xl text-xs font-semibold transition-all duration-200 group relative",
                    isActive
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/30 border border-blue-400/30"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/5"
                  )}
                >
                  <Icon className={cn("h-4 w-4 transition-transform group-hover:scale-110", isActive ? "text-white" : "text-slate-400 group-hover:text-white")} />
                  <span className="truncate">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* System & History Navigation Section */}
        <div className="flex flex-col gap-2 pt-2 border-t border-white/5">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 px-3">
            SYSTEM &amp; SETTINGS
          </span>

          <nav className="flex flex-col gap-1.5">
            {SYSTEM_MENU.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(item.href);

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-200 group relative",
                    isActive
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/30 border border-blue-400/30"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/5"
                  )}
                >
                  <Icon className={cn("h-4 w-4 transition-transform group-hover:scale-110", isActive ? "text-white" : "text-slate-400 group-hover:text-white")} />
                  <span className="truncate">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* User Profile Footer Pill - Dynamic Google Auth User */}
      <div className="pt-4 border-t border-white/10 flex items-center justify-between gap-3">
        {isAuthenticated && user ? (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2.5 overflow-hidden">
              {user.profile_picture ? (
                <img
                  src={user.profile_picture}
                  alt={user.name}
                  className="h-9 w-9 min-w-9 rounded-xl object-cover border border-white/20 shadow-md"
                />
              ) : (
                <div className="h-9 w-9 min-w-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-extrabold text-white text-xs shadow-md border border-white/20">
                  {getInitials(user.name)}
                </div>
              )}
              <div className="flex flex-col leading-tight overflow-hidden">
                <span className="text-xs font-bold text-slate-100 truncate">{user.name}</span>
                <span className="text-[10px] text-emerald-400 font-semibold truncate flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" /> Connected
                </span>
              </div>
            </div>

            <button
              onClick={logout}
              className="p-2 rounded-xl hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={login}
            className="w-full py-2.5 px-3 rounded-2xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20 cursor-pointer"
          >
            <UserIcon className="h-4 w-4" />
            <span>Sign In</span>
          </button>
        )}
      </div>
    </aside>
  );
}
