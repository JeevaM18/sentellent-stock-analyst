"use client"

import { signOut } from "next-auth/react"

export default function LogoutButton() {
  return (
    <button
      onClick={() => signOut()}
      className="px-5 py-2.5 bg-rose-600/90 hover:bg-rose-600 text-white font-medium rounded-xl shadow-md transition-all duration-200 cursor-pointer"
    >
      Sign Out
    </button>
  )
}
