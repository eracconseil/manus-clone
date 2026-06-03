import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ManusClone — AI Agent",
  description: "Autonomous AI agent powered by Claude, Kimi & Qwen",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className="h-full">
      <body className="h-full">{children}</body>
    </html>
  );
}
