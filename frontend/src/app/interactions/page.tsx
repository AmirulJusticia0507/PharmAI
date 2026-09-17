"use client";

import { useEffect, useId, useState } from "react";
import { fetchDrugs, type Drug } from "@/lib/api";

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
  const [suggestions, setSuggestions] = useState<Record<number, Drug[]>>({});
  const [activeIndex, setActiveIndex] = useState<Record<number, number>>({});
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const inputIds = useId();

  const addDrug = () => setDrugs([...drugs, ""]);
  const removeDrug = (i: number) => {
    if (drugs.length <= 2) return;
    setDrugs(drugs.filter((_, idx) => idx !== i));
    setSuggestions(prev => { const n = { ...prev }; delete n[i]; return n; });
    setActiveIndex(prev => { const n = { ...prev }; delete n[i]; return n; });
  };
  const updateDrug = (i: number, val: string) => {
    const next = [...drugs];
    next[i] = val;
    setDrugs(next);
  };

  const fetchSuggestions = async (i: number, query: string) => {
    if (!query.trim()) {
      setSuggestions(prev => ({ ...prev, [i]: [] }));
      return;
    }
    try {
      const data = await fetchDrugs({ search: query, limit: 8 });
      setSuggestions(prev => ({ ...prev, [i]: data }));
      setActiveIndex(prev => ({ ...prev, [i]: 0 }));
    } catch {
      setSuggestions(prev => ({ ...prev, [i]: [] }));
    }
  };

  const handleInputChange = (i: number, val: string) => {
    updateDrug(i, val);
    fetchSuggestions(i, val);
    setOpenIndex(i);
  };

  const selectSuggestion = (i: number, drug: Drug) => {
    updateDrug(i, drug.name);
    setSuggestions(prev => ({ ...prev, [i]: [] }));
    setOpenIndex(null);
  };

  const handleKeyDown = (i: number, e: React.KeyboardEvent) => {
    const items = suggestions[i] || [];
    const current = activeIndex[i] ?? 0;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex(prev => ({ ...prev, [i]: Math.min(current + 1, items.length - 1) }));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex(prev => ({ ...prev, [i]: Math.max(current - 1, 0) }));
    } else if (e.key === "Enter" && items[current]) {
      e.preventDefault();
      selectSuggestion(i, items[current]);
    } else if (e.key === "Escape") {
      setSuggestions(prev => ({ ...prev, [i]: [] }));
      setOpenIndex(null);
    }
  };

  const handleBlur = (i: number) => {
    setTimeout(() => {
      setSuggestions(prev => ({ ...prev, [i]: [] }));
      setOpenIndex(null);
    }, 150);
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
        <div className="interaction-heading"><div><span className="section-kicker">PHARM-AI SAFETY CHECK</span><h1>Minum lebih aman,<br /><em>mulai dari sini.</em></h1><p>Masukkan obat yang dikonsumsi bersamaan. PharmAI akan membantu menemukan potensi interaksi yang perlu diperhatikan.</p></div><div className="safety-mark"><span>✦</span><small>ANALISIS<br />BERBASIS AI</small></div></div>
        <div className="interaction-layout">
          <form onSubmit={handleCheck} className="interaction-form"><div className="form-top"><div><span className="section-kicker">DAFTAR OBAT</span><h2>Apa saja yang Anda konsumsi?</h2></div><span className="drug-counter">{drugs.filter((drug) => drug.trim()).length.toString().padStart(2, "0")} OBAT</span></div><p className="form-helper">Tambahkan minimal dua obat untuk memulai pemeriksaan.</p><div className="drug-inputs">{drugs.map((drug, i) => (
      <div key={i} className="drug-input-row drug-autocomplete">
        <span className="input-index">0{i + 1}</span>
        <input
          type="text"
          value={drug}
          onChange={e => handleInputChange(i, e.target.value)}
          onKeyDown={e => handleKeyDown(i, e)}
          onFocus={() => fetchSuggestions(i, drug)}
          onBlur={() => handleBlur(i)}
          placeholder={`Nama obat ${i + 1}`}
          aria-label={`Nama obat ${i + 1}`}
          autoComplete="off"
        />
        {drugs.length > 2 && (
          <button type="button" onClick={() => removeDrug(i)} aria-label={`Hapus obat ${i + 1}`}>✕</button>
        )}
        {suggestions[i]?.length && openIndex === i && (
          <div className="autocomplete-dropdown" role="listbox">
            {suggestions[i]!.map((d, idx) => (
              <div
                key={d.id}
                className={`autocomplete-item ${idx === (activeIndex[i] ?? 0) ? "highlighted" : ""}`}
                role="option"
                onMouseDown={() => selectSuggestion(i, d)}
              >
                <span className="autocomplete-name">{d.name}</span>
                <div className="autocomplete-meta">
                  {d.category && <span className="autocomplete-category">{d.category}</span>}
                  {d.generic_name && <span className="autocomplete-generic">{d.generic_name}</span>}
                </div>
              </div>
            ))}
            {!suggestions[i]!.length && (
              <div className="autocomplete-empty">Tidak ditemukan</div>
            )}
          </div>
        )}
      </div>
    ))}</div><button type="button" onClick={addDrug} className="add-drug">+ Tambah obat lain</button><button type="submit" disabled={loading} className="primary-action interaction-submit">{loading ? "Menganalisis kombinasi..." : "Periksa interaksi"}<span aria-hidden="true">→</span></button>{error && <div className="interaction-error">{error}</div>}</form>
          <aside className="interaction-aside"><span className="section-kicker">CARA KERJA</span><h3>Informasi yang lebih jelas untuk keputusan yang lebih tenang.</h3><div className="interaction-steps"><div><span>01</span><p>Masukkan semua obat yang sedang dikonsumsi.</p></div><div><span>02</span><p>AI membandingkan kombinasi dan tingkat risikonya.</p></div><div><span>03</span><p>Baca rekomendasi yang relevan untuk langkah berikutnya.</p></div></div><small className="medical-note">Hasil ini bersifat informatif. Selalu konsultasikan perubahan obat dengan tenaga kesehatan.</small></aside>
        </div>
        {result && <section className={`interaction-result safety-${result.overall_safety}`}><div className="result-overview"><div><span className="section-kicker">HASIL PEMERIKSAAN</span><h2>Kombinasi obat Anda</h2><p>{result.summary}</p></div><div className="safety-status"><span className="status-orb">{result.overall_safety === "safe" ? "✓" : "!"}</span><small>STATUS KEAMANAN</small><strong>{result.overall_safety.toUpperCase()}</strong></div></div>{result.interactions.length > 0 && <div className="interaction-list"><div className="result-list-heading"><span>DETAIL YANG PERLU DIPERHATIKAN</span><span>{result.interactions.length.toString().padStart(2, "0")} TEMUAN</span></div>{result.interactions.map((inter, i) => <article key={i} className={`interaction-item severity-${inter.severity}`}><div className="interaction-item-head"><span className="severity-dot" /><strong>{inter.drugs.join(" + ")}</strong><span className="severity-label">{inter.severity}</span></div><p>{inter.description}</p><div className="recommendation"><span>REKOMENDASI</span><p>{inter.recommendation}</p></div></article>)}</div>}</section>}
      </section>
    </main>
  );
}
