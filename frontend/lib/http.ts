/** One place that unwraps the { status, message, data } envelope and throws ApiError on failure. */

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000/api").replace(/\/$/, "");

export type Details = Record<string, string[]>;

export class ApiError extends Error {
  constructor(
    public httpStatus: number,
    public code: string,
    message: string,
    public details?: Details,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface RequestOptions {
  token?: string | null;
  body?: unknown;
  form?: FormData;
  query?: Record<string, string | undefined | null>;
}

export async function request<T>(method: string, path: string, opts: RequestOptions = {}): Promise<T> {
  const url = new URL(`${API_URL}${path}`);
  for (const [key, value] of Object.entries(opts.query ?? {})) {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
  }
  const headers: Record<string, string> = {};
  if (opts.token) headers.Authorization = `Bearer ${opts.token}`;
  let body: BodyInit | undefined;
  if (opts.form) {
    body = opts.form;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  let res: Response;
  try {
    res = await fetch(url, { method, headers, body, cache: "no-store" });
  } catch {
    throw new ApiError(0, "NETWORK_ERROR", "Cannot reach the server");
  }

  let payload: unknown;
  try {
    payload = await res.json();
  } catch {
    throw new ApiError(res.status, "ERROR", res.statusText || "Unexpected response");
  }
  const env = payload as {
    status?: boolean;
    message?: string;
    data?: T;
    error?: { code?: string; details?: Details };
  };
  if (env.status === true) return env.data as T;
  throw new ApiError(res.status, env.error?.code ?? "ERROR", env.message ?? "Request failed", env.error?.details);
}
