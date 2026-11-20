import { NextResponse, type NextRequest } from "next/server";
import { isUsableToken } from "@/lib/session-token";
import { TOKEN_COOKIE } from "@/lib/session";

/**
 * Route guard (Decisions P and T): no cookie, or one that cannot be used, redirects to /login with a safe `next`
 * and removes the stale cookie. This check is optimistic; the Backend stays the authority (a revoked or forged
 * Token that still decodes meets a 401, which lands on /session-expired).
 */
export function proxy(request: NextRequest) {
  const token = request.cookies.get(TOKEN_COOKIE)?.value;
  if (isUsableToken(token)) {
    const headers = new Headers(request.headers);
    headers.set("x-return-path", request.nextUrl.pathname + request.nextUrl.search);
    return NextResponse.next({ request: { headers } });
  }
  const url = new URL("/login", request.url);
  url.searchParams.set("next", request.nextUrl.pathname + request.nextUrl.search);
  const response = NextResponse.redirect(url);
  if (token !== undefined) response.cookies.delete(TOKEN_COOKIE);
  return response;
}

export const config = { matcher: ["/boards/:path*", "/profile/:path*", "/admin/:path*"] };
