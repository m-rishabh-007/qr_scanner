import { useQueryClient } from "@tanstack/react-query";
import * as SecureStore from "expo-secure-store";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import { rawRequest } from "@/api/client";
import type { LoginResponse, Tokens } from "@/types/api";

const ACCESS_KEY = "reviewflow.access";
const REFRESH_KEY = "reviewflow.refresh";

type AuthContextValue = {
  ready: boolean;
  accessToken: string | null;
  isSigningOut: boolean;
  signIn(email: string, password: string): Promise<boolean>;
  signOut(): Promise<void>;
  refresh(): Promise<string | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [ready, setReady] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const signingOutRef = useRef(false);
  const sessionGenerationRef = useRef(0);

  useEffect(() => {
    let active = true;
    void SecureStore.getItemAsync(ACCESS_KEY)
      .then((token) => {
        if (active) setAccessToken(token);
      })
      .catch(() => undefined)
      .finally(() => {
        if (active) setReady(true);
      });
    return () => {
      active = false;
    };
  }, []);

  const persist = useCallback(async (tokens: Tokens, generation: number) => {
    if (generation !== sessionGenerationRef.current || signingOutRef.current) return false;
    try {
      await Promise.all([
        SecureStore.setItemAsync(ACCESS_KEY, tokens.access),
        SecureStore.setItemAsync(REFRESH_KEY, tokens.refresh)
      ]);
    } catch (error) {
      await Promise.allSettled([
        SecureStore.deleteItemAsync(ACCESS_KEY),
        SecureStore.deleteItemAsync(REFRESH_KEY)
      ]);
      throw error;
    }

    if (generation !== sessionGenerationRef.current || signingOutRef.current) {
      await Promise.allSettled([
        SecureStore.deleteItemAsync(ACCESS_KEY),
        SecureStore.deleteItemAsync(REFRESH_KEY)
      ]);
      return false;
    }

    setAccessToken(tokens.access);
    return true;
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    if (signingOutRef.current) return false;
    sessionGenerationRef.current += 1;
    const generation = sessionGenerationRef.current;

    const result = await rawRequest<LoginResponse>("/api/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    if (generation !== sessionGenerationRef.current || signingOutRef.current) return false;
    await queryClient.cancelQueries({}, { silent: true });
    if (generation !== sessionGenerationRef.current || signingOutRef.current) return false;

    queryClient.clear();
    return persist(result, generation);
  }, [persist, queryClient]);

  const signOut = useCallback(async () => {
    if (signingOutRef.current) return;
    signingOutRef.current = true;
    setIsSigningOut(true);
    sessionGenerationRef.current += 1;
    const currentAccessToken = accessToken;

    try {
      const refreshTokenPromise = SecureStore.getItemAsync(REFRESH_KEY).catch(() => null);
      await queryClient.cancelQueries({}, { silent: true }).catch(() => undefined);
      queryClient.clear();
      setAccessToken(null);

      const refreshToken = await refreshTokenPromise;
      await Promise.allSettled([
        SecureStore.deleteItemAsync(ACCESS_KEY),
        SecureStore.deleteItemAsync(REFRESH_KEY)
      ]);

      if (currentAccessToken && refreshToken) {
        void rawRequest("/api/auth/logout/", {
          method: "POST",
          headers: { Authorization: `Bearer ${currentAccessToken}` },
          body: JSON.stringify({ refresh: refreshToken })
        }).catch(() => undefined);
      }
    } finally {
      signingOutRef.current = false;
      setIsSigningOut(false);
    }
  }, [accessToken, queryClient]);

  const refresh = useCallback(async () => {
    if (signingOutRef.current) return null;
    const generation = sessionGenerationRef.current;

    try {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
      if (!refreshToken || generation !== sessionGenerationRef.current || signingOutRef.current) return null;
      const result = await rawRequest<Tokens>("/api/auth/refresh/", {
        method: "POST",
        body: JSON.stringify({ refresh: refreshToken })
      });
      const stored = await persist(
        { access: result.access, refresh: result.refresh ?? refreshToken },
        generation
      );
      return stored ? result.access : null;
    } catch {
      if (generation === sessionGenerationRef.current && !signingOutRef.current) await signOut();
      return null;
    }
  }, [persist, signOut]);

  const value = useMemo(
    () => ({ ready, accessToken, isSigningOut, signIn, signOut, refresh }),
    [ready, accessToken, isSigningOut, signIn, signOut, refresh]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
