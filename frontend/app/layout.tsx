import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "@/styles/tokens.css";
import "@/styles/globals.css";

export const metadata: Metadata = { title: "Kanban", description: "Kanban task management" };
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
