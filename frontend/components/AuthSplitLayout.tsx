import type { ReactNode } from "react";

/** Server Component: brand panel beside an elevated, rounded form card. The brand panel is hidden below 960px. */
export function AuthSplitLayout({ children }: { children: ReactNode }) {
  return (
    <main className="auth">
      <aside className="auth-brand" aria-hidden="true">
        <div className="brand-mark">K</div>
        <div>
          <h2>Plan the work. Move it forward.</h2>
          <p>Boards, cards and comments in one calm place, from your phone to your desk.</p>
        </div>
        <small>Kanban Task Management</small>
      </aside>
      <section className="auth-form-side">
        <div className="auth-card">
          <div className="auth-mobile-brand">
            <div className="brand-mark">K</div>
            <span>Kanban</span>
          </div>
          {children}
        </div>
      </section>
    </main>
  );
}
