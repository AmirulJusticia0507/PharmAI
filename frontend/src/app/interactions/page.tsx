"use client";

import { useState } from "react";

interface Interaction {
  drugs: string[];
  severity: "high" | "medium" | "low";
  description: string;
  recommendation: string;
}

interface InteractionResult {
  interactions: Interaction[];
  overall_safety: string;
  summary: string;
}

const SEVERITY_COLOR = {
  high: "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-green-100 text-green-700",
};

const SAFETY_COLOR: Record<string, string> = {
  safe: "bg-green-100 text-green-700",
  caution: "bg-yellow-100 text-yellow-700",
  unsafe: "bg-red-100 text-red-700",
};

export default function InteractionsPage() {
  const [drugs, setDrugs] = useState(["", ""]);
  const [result, setResult] = useState<InteractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addDrug = () => setDrugs([...drugs, ""]);
  const removeDrug = (i: number) => {
    if (drugs.length <= 2) return;
    setDrugs(drugs.filter((_, idx) => idx !== i));
  };
  const updateDrug = (i: number, val: string) => {
    const next = [...drugs];
    next[i] = val;
    setDrugs(next);
  };

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    const validDrugs = drugs.filter((d) => d.trim());
    if (validDrugs.length < 2) {
      setError("Masukkan minimal 2 obat");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/ai/interactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ drug_names: validDrugs }),
      });
      if (!res.ok) throw new Error("Gagal cek interaksi");
      const data = await res.json();
      setResult(data);
    } catch {
      setError("Gagal menganalisis interaksi obat");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="/" className="text-xl font-bold text-blue-600">
            PharmAI
          </a>
          <div className="flex gap-4 text-sm">
            <a href="/drugs" className="hover:text-blue-600">
              Obat
            </a>
            <a href="/scan" className="hover:text-blue-600">
              Scan Pil
            </a>
            <a href="/interactions" className="text-blue-600 font-medium">
              Interaksi
            </a>
            <a href="/ocr" className="hover:text-blue-600">
              Resep
            </a>
          </div>
        </div>
      </nav>

      <section className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">Cek Interaksi Obat</h1>
        <p className="text-gray-600 mb-6">
          Masukkan nama obat yang dikonsumsi bersamaan untuk mengecek potensi
          interaksi.
        </p>

        <form onSubmit={handleCheck} className="space-y-3 mb-6">
          {drugs.map((drug, i) => (
            <div key={i} className="flex gap-2">
              <input
                type="text"
                value={drug}
                onChange={(e) => updateDrug(i, e.target.value)}
                placeholder={`Obat ${i + 1}`}
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {drugs.length > 2 && (
                <button
                  type="button"
                  onClick={() => removeDrug(i)}
                  className="text-gray-400 hover:text-red-500 px-2"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={addDrug}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              + Tambah Obat
            </button>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:bg-blue-400"
          >
            {loading ? "Menganalisis..." : "Cek Interaksi"}
          </button>
        </form>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="font-medium">Keamanan:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  SAFETY_COLOR[result.overall_safety] || "bg-gray-100"
                }`}
              >
                {result.overall_safety.toUpperCase()}
              </span>
            </div>

            <p className="text-gray-700">{result.summary}</p>

            {result.interactions.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold">Detail Interaksi:</h3>
                {result.interactions.map((inter, i) => (
                  <div key={i} className="bg-white border rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium">
                        {inter.drugs.join(" + ")}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          SEVERITY_COLOR[inter.severity]
                        }`}
                      >
                        {inter.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">
                      {inter.description}
                    </p>
                    <p className="text-sm text-blue-600">
                      Rekomendasi: {inter.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
