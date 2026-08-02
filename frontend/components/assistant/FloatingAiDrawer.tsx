"use client";

import React, { useState } from "react";
import { Sparkles, X, Send, Bot, Loader2 } from "lucide-react";
import { api } from "@/services/api";

export function FloatingAiDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: "user" | "ai"; text: string }>>([
    { sender: "ai", text: "Hello! I am your Sentellent Alpha AI Assistant. Ask me any stock analysis or market question!" },
  ]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input;
    setInput("");
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setLoading(true);

    try {
      const res = await api.sendAgentMessage(userText);
      setMessages((prev) => [...prev, { sender: "ai", text: res.answer || "No response received." }]);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Failed to reach AI assistant.";
      setMessages((prev) => [...prev, { sender: "ai", text: `Error: ${errorMsg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-3 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white font-semibold text-sm shadow-xl shadow-blue-500/25 hover:scale-105 transition-all"
      >
        <Sparkles className="h-4 w-4 animate-spin-slow" />
        <span>Ask AI</span>
      </button>

      {/* Slide-out Drawer */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] h-[500px] max-h-[70vh] rounded-3xl glass-panel border border-white/15 p-4 shadow-2xl flex flex-col justify-between animate-in slide-in-from-bottom duration-300">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-blue-400" />
              <span className="font-semibold text-slate-100 text-sm">Quick AI Assistant</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="p-1 text-slate-400 hover:text-white rounded-lg">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto py-3 space-y-3">
            {messages.map((m, idx) => (
              <div key={idx} className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                    m.sender === "user"
                      ? "bg-blue-600 text-white shadow-md shadow-blue-500/10"
                      : "bg-white/10 text-slate-200 border border-white/10"
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/10 text-blue-400 rounded-2xl px-3.5 py-2 text-xs items-center gap-2 border border-white/10 flex">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>AI is reasoning...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSend} className="flex items-center gap-2 pt-2 border-t border-white/10">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition-all"
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
