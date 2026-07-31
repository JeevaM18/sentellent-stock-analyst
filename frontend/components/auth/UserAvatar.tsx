"use client"

import { useSession } from "next-auth/react"
import LoginButton from "./LoginButton"
import LogoutButton from "./LogoutButton"

export default function UserAvatar() {
  const { data: session, status } = useSession()

  if (status === "loading") {
    return (
      <div className="flex items-center justify-center p-8 bg-slate-900/60 rounded-2xl border border-slate-800 backdrop-blur-md">
        <div className="animate-pulse flex space-x-4 items-center">
          <div className="rounded-full bg-slate-700 h-12 w-12"></div>
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-slate-700 rounded w-24"></div>
            <div className="h-3 bg-slate-700 rounded w-32"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!session || !session.user) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-slate-900/80 rounded-2xl border border-slate-800/80 shadow-2xl max-w-md w-full text-center backdrop-blur-md">
        <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mb-5 border border-blue-500/20">
          <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Sentellent Stock Analyst</h2>
        <p className="text-slate-400 text-sm mb-6 max-w-sm">
          Welcome! Sign in with your Google account to access your personalized stock insights, portfolio tracking, and RAG search.
        </p>
        <LoginButton />
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center p-8 bg-slate-900/90 rounded-2xl border border-slate-800 shadow-2xl max-w-md w-full text-center backdrop-blur-md">
      {session.user.image ? (
        <img
          src={session.user.image}
          alt={session.user.name || "User Avatar"}
          className="w-20 h-20 rounded-full border-2 border-blue-500/50 shadow-md mb-4 object-cover"
        />
      ) : (
        <div className="w-20 h-20 rounded-full bg-blue-600 flex items-center justify-center text-2xl font-bold text-white mb-4">
          {session.user.name?.charAt(0) || "U"}
        </div>
      )}
      <h2 className="text-2xl font-bold text-white mb-1">{session.user.name}</h2>
      <p className="text-slate-400 text-sm mb-6">{session.user.email}</p>
      
      <div className="w-full pt-4 border-t border-slate-800 flex items-center justify-between">
        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          Session Active
        </span>
        <LogoutButton />
      </div>
    </div>
  )
}
