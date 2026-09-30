import type { Metadata, Viewport } from "next";
import "./globals.css";
import PwaControls from "./PwaControls";
import ThemeToggle from "./ThemeToggle";

export const metadata: Metadata = {
  title: "PharmAI - AI Analisis Obat",
  description: "Sistem analisis obat berbasis Artificial Intelligence",
  applicationName: "PharmAI",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "PharmAI",
  },
};

export const viewport: Viewport = {
  themeColor: "#153e34",
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
      <body>{children}<PwaControls /><ThemeToggle /></body>
    </html>
  );
}
