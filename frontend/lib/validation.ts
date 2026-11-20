/** Identity validation; mirrors backend/app/common/validation.py (V10, Property 42). */
const USERNAME_RE = /^[a-z0-9_.]{3,30}$/;
const EMAIL_RE = /^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/;
export const EMAIL_MAX = 255;

export function isUsername(value: string): boolean {
  return USERNAME_RE.test(value);
}

export function isEmail(value: string): boolean {
  return value.length <= EMAIL_MAX && EMAIL_RE.test(value);
}

export type IdentifierKind = "email" | "username";

/** "email" when the lower-cased value has an @ and the email shape, "username" when it has none and matches the format, else null. */
export function classifyIdentifier(raw: string): { kind: IdentifierKind; value: string } | null {
  const value = raw.trim().toLowerCase();
  if (value.includes("@")) return isEmail(value) ? { kind: "email", value } : null;
  return isUsername(value) ? { kind: "username", value } : null;
}
