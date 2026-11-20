"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState, type ChangeEvent, type FormEvent } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseAlert, BaseField, BaseInput } from "@/components/shared/BaseField";
import { formatCountdown, useCountdown } from "@/hooks/useCountdown";
import { api } from "@/lib/api";
import { ApiError } from "@/lib/http";
import { safeReturnPath } from "@/lib/return-path";
import { setSession } from "@/lib/session";
import { classifyIdentifier, isEmail, isUsername } from "@/lib/validation";

type Mode = "login" | "register";

const COPY = {
  login: { title: "Welcome back", sub: "Log in to your boards.", cta: "Log in", other: "No account yet?", link: "/register", linkText: "Register" },
  register: { title: "Create your account", sub: "It takes a minute.", cta: "Register", other: "Already registered?", link: "/login", linkText: "Log in" },
} as const;

const GENERIC_LOGIN_ERROR = "Invalid username, email or password.";
type Values = { full_name: string; identifier: string; username: string; email: string; password: string };

/** One form for both modes. Login takes a Username or Email; register takes both separately (Decisions M and N). */
export function AuthForm({ mode, next }: { mode: Mode; next?: string | null }) {
  const router = useRouter();
  const copy = COPY[mode];
  const [values, setValues] = useState<Values>({ full_name: "", identifier: "", username: "", email: "", password: "" });
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [wait, setWait] = useState<number | null>(null);
  const left = useCountdown(wait);
  const blocked = left > 0;
  // A blocked availability check stops the on-blur checks until the wait ends (Req 20.16).
  const availabilityPausedUntil = useRef(0);

  const set = (key: keyof Values) => (e: ChangeEvent<HTMLInputElement>) => setValues((v) => ({ ...v, [key]: e.target.value }));

  async function checkAvailability(field: "username" | "email") {
    const value = values[field].trim();
    const valid = field === "username" ? isUsername(value.toLowerCase()) : isEmail(value.toLowerCase());
    if (!value || !valid || Date.now() < availabilityPausedUntil.current) return;
    try {
      const result = await api.auth.availability({ [field]: value });
      if (result[field]?.available === false) {
        setErrors((e) => ({ ...e, [field]: [field === "username" ? "This username is already taken." : "This email is already registered."] }));
      }
    } catch (err) {
      if (err instanceof ApiError && err.httpStatus === 429) availabilityPausedUntil.current = Date.now() + (err.retryAfter ?? 60) * 1000;
      // any failure stays silent: the 409 on submit is authoritative
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErrors({});
    setFormError(null);
    if (mode === "login") {
      // No request is sent for a value that is neither a Username nor an Email (Req 1.39, 1.40).
      if (!classifyIdentifier(values.identifier)) {
        const message = values.identifier.includes("@") ? "Enter a valid email address." : "Enter a valid username or email.";
        setErrors({ identifier: [message] });
        return;
      }
      if (!values.password) {
        setErrors({ password: ["password is required"] });
        return;
      }
    }
    setBusy(true);
    try {
      const result =
        mode === "login"
          ? await api.auth.login({ identifier: values.identifier.trim(), password: values.password })
          : await api.auth.register({
              full_name: values.full_name,
              username: values.username.trim(),
              email: values.email.trim(),
              password: values.password,
            });
      setSession(result.token, result.user);
      router.push(safeReturnPath(next));
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError && err.httpStatus === 429) {
        setWait(err.retryAfter ?? 60);
      } else if (err instanceof ApiError && mode === "login" && err.httpStatus === 401) {
        setFormError(GENERIC_LOGIN_ERROR);
      } else if (err instanceof ApiError) {
        // field errors come from error.details; anything else is a form-level message
        if (err.details && Object.keys(err.details).length) setErrors(err.details);
        else setFormError(err.message);
      } else {
        setFormError("Something went wrong. Try again.");
      }
    } finally {
      setBusy(false);
    }
  }

  const field = (id: keyof Values, label: string, opts: { type?: string; autoComplete?: string; onBlur?: () => void } = {}) => (
    <BaseField label={label} htmlFor={id} errors={errors[id]}>
      <BaseInput
        id={id}
        name={id}
        type={opts.type ?? "text"}
        autoComplete={opts.autoComplete}
        value={values[id]}
        onChange={set(id)}
        onBlur={opts.onBlur}
        aria-invalid={errors[id] ? true : undefined}
        aria-describedby={errors[id] ? `${id}-error` : undefined}
      />
    </BaseField>
  );

  return (
    <>
      <h1 className="text-xl font-bold">{copy.title}</h1>
      <p className="mt-1 mb-6 text-ink-muted">{copy.sub}</p>
      <form method="post" className="flex flex-col gap-4" onSubmit={onSubmit} noValidate>
        {formError && <BaseAlert>{formError}</BaseAlert>}
        {blocked && <BaseAlert>Too many attempts. Try again in {formatCountdown(left)}.</BaseAlert>}
        {mode === "register" && field("full_name", "Full name", { autoComplete: "name" })}
        {mode === "login" && field("identifier", "Username or email", { autoComplete: "username" })}
        {mode === "register" && field("username", "Username", { autoComplete: "username", onBlur: () => void checkAvailability("username") })}
        {mode === "register" && field("email", "Email", { type: "email", autoComplete: "email", onBlur: () => void checkAvailability("email") })}
        {field("password", "Password", { type: "password", autoComplete: mode === "login" ? "current-password" : "new-password" })}
        <BaseButton type="submit" block disabled={busy || blocked}>
          {busy ? "Please wait…" : copy.cta}
        </BaseButton>
      </form>
      <p className="mt-4 text-center text-sm text-ink-muted">
        {copy.other}{" "}
        <Link href={copy.link} className="font-semibold">
          {copy.linkText}
        </Link>
      </p>
    </>
  );
}
