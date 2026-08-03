import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { authenticatedRequest, rawRequest } from "@/api/client";
import { useAuth } from "@/store/auth";
import type { DomainOption, FeedbackItem, Location, Overview } from "@/types/api";

function useAuthedFetcher() {
  const { ready, accessToken, isSigningOut, refresh } = useAuth();
  const enabled = ready && !!accessToken && !isSigningOut;

  const fetcher = <T,>(path: string, init?: RequestInit) => {
    if (!accessToken || isSigningOut) return Promise.reject(new Error("Authentication required"));
    return authenticatedRequest<T>(path, accessToken, refresh, init);
  };

  return { enabled, fetcher };
}

export function useOverview(period: number) {
  const { enabled, fetcher } = useAuthedFetcher();
  return useQuery({
    queryKey: ["overview", period],
    queryFn: ({ signal }) => fetcher<Overview>(`/api/merchant/analytics/overview/?period=${period}`, { signal }),
    enabled
  });
}

export function useFeedback(period: number, classification = "") {
  const { enabled, fetcher } = useAuthedFetcher();
  const suffix = classification ? `&classification=${classification}` : "";
  return useQuery({
    queryKey: ["feedback", period, classification],
    queryFn: ({ signal }) => fetcher<{ results?: FeedbackItem[] } | FeedbackItem[]>(
      `/api/merchant/analytics/feedback/?period=${period}${suffix}`,
      { signal }
    ).then((data) => Array.isArray(data) ? data : data.results ?? []),
    enabled
  });
}

export function useLocation() {
  const { enabled, fetcher } = useAuthedFetcher();
  return useQuery({
    queryKey: ["location"],
    queryFn: ({ signal }) => fetcher<Location | null>("/api/merchant/location/", { signal }),
    enabled
  });
}

export function useDomains() {
  const { enabled, fetcher } = useAuthedFetcher();
  return useQuery({
    queryKey: ["domains"],
    queryFn: ({ signal }) => fetcher<DomainOption[]>("/api/merchant/domains/", { signal }),
    enabled
  });
}

export function useSaveLocation() {
  const { fetcher } = useAuthedFetcher();
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ location, exists }: { location: Partial<Location> & { domain_id: number }; exists: boolean }) => fetcher<Location>("/api/merchant/location/", { method: exists ? "PATCH" : "POST", body: JSON.stringify(location) }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["location"] })
  });
}

export function registerMerchant(input: { email: string; password: string; business_name: string }) {
  return rawRequest<{ detail: string }>("/api/auth/register/", { method: "POST", body: JSON.stringify(input) });
}
