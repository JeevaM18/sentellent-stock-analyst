"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { SessionProvider, useSession, signIn, signOut } from "next-auth/react";
import { AuthService, UserResponse, setAuthToken } from "@/services/api";

export interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: () => Promise<void>;
  loginAsEvaluator: (email: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  syncUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: async () => {},
  loginAsEvaluator: async () => {},
  logout: async () => {},
  syncUser: async () => {},
});

function AuthProviderInternal({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const [dbUser, setDbUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const syncUser = async () => {
    const email = session?.user?.email || dbUser?.email || "jeeva59128@gmail.com";
    const name = session?.user?.name || dbUser?.name || "Jeeva M";
    const picture = session?.user?.image || dbUser?.profile_picture;

    try {
      const googleToken = (session as unknown as { auth?: { googleIdToken?: string } })?.auth?.googleIdToken;
      setAuthToken(googleToken || "dev-sentellent-auth-token");

      // Call backend POST /api/auth/sync
      const synced = await AuthService.sync({
        email,
        name,
        profile_picture: picture || undefined,
      });

      if (synced) {
        setDbUser(synced);
      }
    } catch (err) {
      console.warn("Backend user sync warning:", err);
      setDbUser({
        id: email,
        email: email,
        name: name,
        profile_picture: picture || undefined,
        created: false,
      });
    }
  };

  useEffect(() => {
    let isMounted = true;
    async function initAuth() {
      if (status === "loading") return;

      if (status === "authenticated" && session?.user?.email) {
        await syncUser();
      }
      if (isMounted) setLoading(false);
    }

    initAuth();
    return () => {
      isMounted = false;
    };
  }, [session, status]);

  const handleLogin = async () => {
    setLoading(true);
    try {
      // Always try real Google OAuth first — this redirects to Google consent screen
      await signIn("google", { callbackUrl: "/" });
    } catch {
      // If Google provider is not configured, fall back to dev credentials
      try {
        await signIn("google-dev", { redirect: true, callbackUrl: "/" });
      } catch {
        console.warn("All sign-in providers failed");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluatorLogin = async (demoKey: string, demoName: string) => {
    setLoading(true);
    try {
      // 1. Sign in via NextAuth demo-access CredentialsProvider
      await signIn("demo-access", {
        demoUser: demoKey,
        redirect: false,
      });

      // 2. Provision/fetch demo user in PostgreSQL backend
      const synced = await AuthService.demoLogin(demoKey);
      if (synced) {
        setDbUser(synced);
      }
    } catch (err) {
      console.warn("Evaluator demo login fallback:", err);
      const isNaga = demoKey.toLowerCase().includes("naga");
      const email = isNaga ? "naga.demo@sentellent.ai" : "hari.demo@sentellent.ai";
      setDbUser({
        id: email,
        email: email,
        name: demoName,
        created: false,
      });
    } finally {
      setLoading(false);
      window.location.href = "/";
    }
  };

  const handleLogout = async () => {
    setDbUser(null);
    setAuthToken("dev-sentellent-auth-token");
    try {
      await signOut({ redirect: false });
    } catch (err) {
      console.warn("SignOut warning:", err);
    }
    window.location.href = "/";
  };

  const isAuth = Boolean(dbUser) || (status === "authenticated" && Boolean(session?.user?.email));

  const value: AuthContextType = {
    user: isAuth
      ? dbUser || {
          id: session?.user?.email || "jeeva59128@gmail.com",
          email: session?.user?.email || "jeeva59128@gmail.com",
          name: session?.user?.name || "Jeeva M",
          profile_picture: session?.user?.image || undefined,
        }
      : null,
    isAuthenticated: isAuth,
    loading: status === "loading" && !dbUser,
    login: handleLogin,
    loginAsEvaluator: handleEvaluatorLogin,
    logout: handleLogout,
    syncUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AuthProviderInternal>{children}</AuthProviderInternal>
    </SessionProvider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
