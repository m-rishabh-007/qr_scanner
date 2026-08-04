import { describe, expect, it } from "@jest/globals";

import { readJsonPayload } from "./response";

function response(status: number, body: string, ok = status >= 200 && status < 300) {
  return {
    status,
    ok,
    text: async () => body
  };
}

describe("readJsonPayload", () => {
  it("normalizes an empty successful response to null", async () => {
    await expect(readJsonPayload(response(200, ""))).resolves.toBeNull();
  });

  it("preserves an explicit JSON null", async () => {
    await expect(readJsonPayload(response(200, "null"))).resolves.toBeNull();
  });

  it("parses a normal JSON object", async () => {
    await expect(readJsonPayload(response(200, '{"id":1}'))).resolves.toEqual({ id: 1 });
  });

  it("rejects malformed JSON returned with a successful status", async () => {
    await expect(readJsonPayload(response(200, "not-json"))).rejects.toThrow("Server returned invalid JSON.");
  });

  it("lets request error handling use the HTTP status for a non-JSON error body", async () => {
    await expect(readJsonPayload(response(502, "Bad Gateway", false))).resolves.toBeNull();
  });
});
