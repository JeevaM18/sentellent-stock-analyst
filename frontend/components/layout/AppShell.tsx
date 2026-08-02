"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { CommandKModal } from "@/components/common/CommandKModal";
import { FloatingAiDrawer } from "@/components/assistant/FloatingAiDrawer";
import { useAuth } from "@/components/providers/AuthProvider";
import LoginPage from "@/components/auth/LoginPage";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const [isCommandKOpen, setIsCommandKOpen] = useState(false);

  // Eliminate flash of dashboard: if loading or unauthenticated, show ONLY the Login Page immediately
  if (loading || !isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen bg-[#050816] text-slate-100 bg-mesh-radial flex flex-col font-sans">
      <Sidebar />
      <Header onOpenCommandK={() => setIsCommandKOpen(true)} />

      <main className="ml-72 mr-4 mb-8 flex-1">
        {children}
      </main>

      <CommandKModal isOpen={isCommandKOpen} onClose={() => setIsCommandKOpen(false)} />
      <FloatingAiDrawer />
    </div>
  );
}
