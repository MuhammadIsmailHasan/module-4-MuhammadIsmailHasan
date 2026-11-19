import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, request } from "@/lib/http";
import { decodeToken } from "@/lib/session";

function mockFetch(status: number, body: unknown) {
  const fn = vi.fn().mockResolvedValue({ status, statusText: "x", json: async () => body });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals());

describe("request", () => {
  it("returns data when status is true and sends the bearer token", async () => {
    const fn = mockFetch(200, { status: true, message: "OK", data: { id: 1 } });
    const data = await request<{ id: number }>("GET", "/boards", { token: "tok", query: { search: "a b", skip: undefined } });
    expect(data).toEqual({ id: 1 });
    const [url, init] = fn.mock.calls[0];
    expect(String(url)).toContain("/boards?search=a+b");
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer tok");
  });

  it("throws ApiError with code, message and details when status is false", async () => {
    mockFetch(400, { status: false, message: "Validation failed", error: { code: "VALIDATION_ERROR", details: { content: ["content is required"] } } });
    const err = await request("POST", "/x", { body: {} }).catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err).toMatchObject({ httpStatus: 400, code: "VALIDATION_ERROR", message: "Validation failed", details: { content: ["content is required"] } });
  });

  it("maps a network failure to NETWORK_ERROR", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("down")));
    await expect(request("GET", "/x")).rejects.toMatchObject({ code: "NETWORK_ERROR", httpStatus: 0 });
  });

  it("sends JSON bodies with a content type", async () => {
    const fn = mockFetch(201, { status: true, message: "m", data: null });
    await request("POST", "/x", { body: { a: 1 } });
    expect(fn.mock.calls[0][1].body).toBe('{"a":1}');
    expect(fn.mock.calls[0][1].headers["Content-Type"]).toBe("application/json");
  });
});

describe("decodeToken", () => {
  it("reads sub, role and exp from a JWT payload", () => {
    const t = `h.${btoa(JSON.stringify({ sub: "u1", role: "manager", exp: 5 }))}.s`;
    expect(decodeToken(t)).toEqual({ sub: "u1", role: "manager", exp: 5 });
  });
  it("returns null for garbage", () => {
    expect(decodeToken("nope")).toBeNull();
  });
});
