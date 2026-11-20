import { NextResponse, type NextRequest } from "next/server";
import { safeReturnPath } from "@/lib/return-path";
import { TOKEN_COOKIE } from "@/lib/session";

/** Landing for a Token the Backend rejected: drop the cookie, then go to /login (never anywhere else, Req 1.59). */
export function GET(request: NextRequest) {
  const url = new URL("/login", request.url);
  const next = request.nextUrl.searchParams.get("next");
  if (next && safeReturnPath(next) === next) url.searchParams.set("next", next);
  const response = NextResponse.redirect(url);
  response.cookies.delete(TOKEN_COOKIE);
  return response;
}
