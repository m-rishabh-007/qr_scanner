import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { authenticatedRequest, rawRequest } from "@/api/client";
import { useAuth } from "@/store/auth";
import type { DomainOption, FeedbackItem, Location, Overview } from "@/types/api";

function useAuthedFetcher() {
  const { accessToken, refresh } = useAuth();
  if (!accessToken) throw new Error("Authentication required");
  return <T,>(path: string, init?: RequestInit) => authenticatedRequest<T>(path, accessToken, refresh, init);
}

export function useOverview(period: number) {
  const fetcher = useAuthedFetcher();
  return useQuery({ queryKey: ["overview", period], queryFn: () => fetcher<Overview>(`/api/merchant/analytics/overview/?period=${period}`) });
}

export function useFeedback(period: number, classification = "") {
  const fetcher = useAuthedFetcher();
  const suffix = classification ? `&classification=${classification}` : "";
  return useQuery({ queryKey: ["feedback", period, classification], queryFn: () => fetcher<{ results?: FeedbackItem[] } | FeedbackItem[]>(`/api/merchant/analytics/feedback/?period=${period}${suffix}`).then((data) => Array.isArray(data) ? data : data.results ?? []) });
}

export function useLocation() {
  const fetcher = useAuthedFetcher();
  return useQuery({ queryKey: ["location"], queryFn: () => fetcher<Location | null>("/api/merchant/location/") });
}

export function useDomains() {
  const fetcher = useAuthedFetcher();
  return useQuery({ queryKey: ["domains"], queryFn: () => fetcher<DomainOption[]>("/api/merchant/domains/") });
}

export function useSaveLocation() {
  const fetcher = useAuthedFetcher();
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ location, exists }: { location: Partial<Location> & { domain_id: number }; exists: boolean }) => fetcher<Location>("/api/merchant/location/", { method: exists ? "PATCH" : "POST", body: JSON.stringify(location) }),
    onSuccess: (value) => client.setQueryData(["location"], value)
  });
}

export function registerMerchant(input: { email: string; password: string; business_name: string }) {
  return rawRequest<{ detail: string }>("/api/auth/register/", { method: "POST", body: JSON.stringify(input) });
}
