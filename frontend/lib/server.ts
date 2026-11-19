/** Server Component data access: forwards the Token cookie, redirects to login on 401. */
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, request } from "./http";
import { TOKEN_COOKIE } from "./session";

export async function serverToken(): Promise<string | null> {
  return (await cookies()).get(TOKEN_COOKIE)?.value ?? null;
}

export async function serverGet<T>(path: string, query?: Record<string, string | undefined>): Promise<T> {
  const token = await serverToken();
  try {
    return await request<T>("GET", path, { token, query });
  } catch (err) {
    if (err instanceof ApiError && err.httpStatus === 401 && token) redirect("/login");
    throw err;
  }
}
