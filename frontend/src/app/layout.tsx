import type { Metadata } from "next";
import "./globals.css";
import ThemeToggle from "./ThemeToggle";

export const metadata: Metadata = {
  title: "PharmAI - AI Analisis Obat",
  description: "Sistem analisis obat berbasis Artificial Intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: `
          try {
            const saved = localStorage.getItem("pharmai-theme");
            document.documentElement.dataset.theme = saved ||
              (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
          } catch (_) {}
        ` }} />
      </head>
      <body>{children}<ThemeToggle /></body>
    </html>
  );
}
