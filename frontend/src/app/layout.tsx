import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="id">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
