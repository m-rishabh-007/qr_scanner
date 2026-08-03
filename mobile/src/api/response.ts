type JsonResponse = Pick<Response, "ok" | "status" | "text">;

export async function readJsonPayload(response: JsonResponse): Promise<unknown> {
  if (response.status === 204 || response.status === 205) return null;

  const body = await response.text();
  if (!body.trim()) return null;

  try {
    return JSON.parse(body) as unknown;
  } catch {
    if (!response.ok) return null;
    throw Object.assign(new Error("Server returned invalid JSON."), { status: response.status });
  }
}
