"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { api } from "@/lib/api";
import { ApiError } from "@/lib/http";
import { setSession } from "@/lib/session";

type Mode = "login" | "register";

const COPY = {
  login: { title: "Welcome back", sub: "Log in to your boards.", cta: "Log in", other: "No account yet?", link: "/register", linkText: "Register" },
  register: { title: "Create your account", sub: "It takes a minute.", cta: "Register", other: "Already registered?", link: "/login", linkText: "Log in" },
} as const;

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const copy = COPY[mode];
  const [values, setValues] = useState({ full_name: "", login_identifier: "", password: "" });
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const set = (key: keyof typeof values) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setValues((v) => ({ ...v, [key]: e.target.value }));

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setFormError(null);
    try {
      const result =
        mode === "login"
          ? await api.auth.login({ login_identifier: values.login_identifier, password: values.password })
          : await api.auth.register(values);
      setSession(result.token, result.user);
      router.push("/boards");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
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

  const field = (id: keyof typeof values, label: string, type = "text", autoComplete?: string) => (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        name={id}
        type={type}
        className="input"
        autoComplete={autoComplete}
        value={values[id]}
        onChange={set(id)}
        aria-invalid={errors[id] ? true : undefined}
        aria-describedby={errors[id] ? `${id}-error` : undefined}
        required
      />
      {errors[id]?.map((m) => (
        <span key={m} id={`${id}-error`} className="field-error">
          {m}
        </span>
      ))}
    </div>
  );

  return (
    <>
      <h1 className="auth-title">{copy.title}</h1>
      <p className="auth-sub">{copy.sub}</p>
      <form className="stack" onSubmit={onSubmit} noValidate>
        {formError && (
          <div role="alert" className="form-error">
            {formError}
          </div>
        )}
        {mode === "register" && field("full_name", "Full name", "text", "name")}
        {field("login_identifier", "Email or username", "text", "username")}
        {field("password", "Password", "password", mode === "login" ? "current-password" : "new-password")}
        <BaseButton type="submit" block disabled={busy}>
          {busy ? "Please wait…" : copy.cta}
        </BaseButton>
      </form>
      <p className="auth-switch">
        {copy.other} <Link href={copy.link}>{copy.linkText}</Link>
      </p>
    </>
  );
}
