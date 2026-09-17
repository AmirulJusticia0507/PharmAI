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

const bgColors = {
  safe: "bg-green-50",
  caution: "bg-yellow-50",
  unsafe: "bg-red-50",
};

const textColors = {
  safe: "text-green-600",
  caution: "text-yellow-600",
  unsafe: "text-red-600",
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
    <main className="interaction-shell">
      <nav className="site-nav"><div className="nav-inner"><a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a><div className="nav-links"><a href="/drugs">Database Obat</a><a href="/interactions" className="interactions-nav-active">Interaksi</a><a href="/ocr">Resep</a></div><a href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></a></div></nav>
      <section className="interaction-page">
        <div className="interaction-heading"><div><span className="section-kicker">PHARMAI SAFETY CHECK</span><h1>Minum lebih aman,<br /><em>mulai dari sini.</em></h1><p>Masukkan obat yang dikonsumsi bersamaan. PharmAI akan membantu menemukan potensi interaksi yang perlu diperhatikan.</p></div><div className="safety-mark"><span>✦</span><small>ANALISIS<br />BERBASIS AI</small></div></div>
        <div className="interaction-layout">
          <form onSubmit={handleCheck} className="interaction-form"><div className="form-top"><div><span className="section-kicker">DAFTAR OBAT</span><h2>Apa saja yang Anda konsumsi?</h2></div><span className="drug-counter">{drugs.filter((drug) => drug.trim()).length.toString().padStart(2, "0")} OBAT</span></div><p className="form-helper">Tambahkan minimal dua obat untuk memulai pemeriksaan.</p><div className="drug-inputs">{drugs.map((drug, i) => <div key={i} className="drug-input-row"><span className="input-index">0{i + 1}</span><input type="text" value={drug} onChange={(e) => updateDrug(i, e.target.value)} placeholder={`Nama obat ${i + 1}`} aria-label={`Nama obat ${i + 1}`} />{drugs.length > 2 && <button type="button" onClick={() => removeDrug(i)} aria-label={`Hapus obat ${i + 1}`}>✕</button>}</div>)}</div><button type="button" onClick={addDrug} className="add-drug">+ Tambah obat lain</button><button type="submit" disabled={loading} className="primary-action interaction-submit">{loading ? "Menganalisis kombinasi..." : "Periksa interaksi"}<span aria-hidden="true">→</span></button>{error && <div className="interaction-error">{error}</div>}</form>
          <aside className="interaction-aside"><span className="section-kicker">CARA KERJA</span><h3>Informasi yang lebih jelas untuk keputusan yang lebih tenang.</h3><div className="interaction-steps"><div><span>01</span><p>Masukkan semua obat yang sedang dikonsumsi.</p></div><div><span>02</span><p>AI membandingkan kombinasi dan tingkat risikonya.</p></div><div><span>03</span><p>Baca rekomendasi yang relevan untuk langkah berikutnya.</p></div></div><small className="medical-note">Hasil ini bersifat informatif. Selalu konsultasikan perubahan obat dengan tenaga kesehatan.</small></aside>
        </div>
        {result && <section className={`interaction-result safety-${result.overall_safety}`}><div className="result-overview"><div><span className="section-kicker">HASIL PEMERIKSAAN</span><h2>Kombinasi obat Anda</h2><p>{result.summary}</p></div><div className="safety-status"><span className="status-orb">{result.overall_safety === "safe" ? "✓" : "!"}</span><small>STATUS KEAMANAN</small><strong>{result.overall_safety.toUpperCase()}</strong></div></div>{result.interactions.length > 0 && <div className="interaction-list"><div className="result-list-heading"><span>DETAIL YANG PERLU DIPERHATIKAN</span><span>{result.interactions.length.toString().padStart(2, "0")} TEMUAN</span></div>{result.interactions.map((inter, i) => <article key={i} className={`interaction-item severity-${inter.severity}`}><div className="interaction-item-head"><span className="severity-dot" /><strong>{inter.drugs.join(" + ")}</strong><span className="severity-label">{inter.severity}</span></div><p>{inter.description}</p><div className="recommendation"><span>REKOMENDASI</span><p>{inter.recommendation}</p></div></article>)}</div>}</section>}
      </section>
    </main>
  );
}
