import * as SecureStore from "expo-secure-store";
import { router } from "expo-router";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { rawRequest } from "@/api/client";
import type { LoginResponse, Tokens } from "@/types/api";

const ACCESS_KEY = "reviewflow.access";
const REFRESH_KEY = "reviewflow.refresh";

type AuthContextValue = {
  ready: boolean;
  accessToken: string | null;
  signIn(email: string, password: string): Promise<void>;
  signOut(): Promise<void>;
  refresh(): Promise<string | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    SecureStore.getItemAsync(ACCESS_KEY).then((token) => {
      setAccessToken(token);
      setReady(true);
    });
  }, []);

  const persist = useCallback(async (tokens: Tokens) => {
    setAccessToken(tokens.access);
    await Promise.all([
      SecureStore.setItemAsync(ACCESS_KEY, tokens.access),
      SecureStore.setItemAsync(REFRESH_KEY, tokens.refresh)
    ]);
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const result = await rawRequest<LoginResponse>("/api/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    await persist(result);
  }, [persist]);

  const signOut = useCallback(async () => {
    const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
    if (accessToken && refreshToken) {
      rawRequest("/api/auth/logout/", {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify({ refresh: refreshToken })
      }).catch(() => undefined);
    }
    setAccessToken(null);
    await Promise.all([SecureStore.deleteItemAsync(ACCESS_KEY), SecureStore.deleteItemAsync(REFRESH_KEY)]);
    router.replace("/(auth)/login");
  }, [accessToken]);

  const refresh = useCallback(async () => {
    const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
    if (!refreshToken) return null;
    try {
      const result = await rawRequest<Tokens>("/api/auth/refresh/", {
        method: "POST",
        body: JSON.stringify({ refresh: refreshToken })
      });
      await persist({ access: result.access, refresh: result.refresh ?? refreshToken });
      return result.access;
    } catch {
      await signOut();
      return null;
    }
  }, [persist, signOut]);

  const value = useMemo(() => ({ ready, accessToken, signIn, signOut, refresh }), [ready, accessToken, signIn, signOut, refresh]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
