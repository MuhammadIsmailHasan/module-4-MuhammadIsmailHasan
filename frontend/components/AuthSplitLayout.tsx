import type { ReactNode } from "react";
import { BrandLogo } from "@/components/shared/BrandLogo";

/** Server Component: brand panel beside an elevated, rounded form card. The brand panel is hidden below 960px. */
export function AuthSplitLayout({ children }: { children: ReactNode }) {
  return (
    <main className="relative grid min-h-screen grid-cols-1 overflow-hidden lg:grid-cols-2">
      <aside
        aria-hidden="true"
        className="relative hidden flex-col overflow-hidden bg-linear-to-br from-brand to-brand-strong p-12 text-on-brand lg:flex"
      >
        <div className="pointer-events-none absolute -top-12 -right-12 size-column rounded-full bg-accent opacity-glow blur-3xl" />
        <div className="pointer-events-none absolute -bottom-12 -left-12 size-column rounded-full bg-on-brand opacity-glow blur-3xl" />
        <div className="relative w-fit rounded-md bg-surface-raised p-3">
          <BrandLogo variant="full" size="lg" />
        </div>
        <div className="relative my-auto flex flex-col gap-4">
          <h2 className="max-w-auth text-2xl font-bold">Plan the work. Move it forward.</h2>
          <p className="max-w-auth opacity-faint">Boards, cards and comments in one calm place, from your phone to your desk.</p>
        </div>
      </aside>
      <section className="flex items-center justify-center p-4 lg:p-8">
        <div className="w-full max-w-auth rounded-lg bg-surface-raised p-6 shadow-hover lg:p-8">
          <div className="mb-6 lg:hidden">
            <BrandLogo variant="full" size="md" />
          </div>
          {children}
        </div>
      </section>
    </main>
  );
}
