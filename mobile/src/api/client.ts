import { API_BASE_URL } from "@/lib/config";

export async function rawRequest<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) }
  });
  const payload = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = (payload as { detail?: string })?.detail ?? `Request failed (${response.status})`;
    throw Object.assign(new Error(message), { status: response.status, payload });
  }
  return payload as T;
}

export async function authenticatedRequest<T>(
  path: string,
  accessToken: string,
  refresh: () => Promise<string | null>,
  init: RequestInit = {}
): Promise<T> {
  try {
    return await rawRequest<T>(path, {
      ...init,
      headers: { ...(init.headers ?? {}), Authorization: `Bearer ${accessToken}` }
    });
  } catch (error) {
    if ((error as { status?: number }).status !== 401) throw error;
    const replacement = await refresh();
    if (!replacement) throw error;
    return rawRequest<T>(path, {
      ...init,
      headers: { ...(init.headers ?? {}), Authorization: `Bearer ${replacement}` }
    });
  }
}
