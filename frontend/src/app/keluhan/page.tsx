"use client";

import { useState } from "react";
import { assessSymptoms, type SymptomAssessment } from "@/lib/api";

const initialForm = { complaint: "", age: "", sex: "", duration: "", existing_conditions: "", current_medicines: "", allergies: "", pregnancy_status: "" };

const urgencyLabel = {
  emergency: "Segera cari pertolongan",
  urgent: "Perlu diperiksa segera",
  routine: "Konsultasi terjadwal",
  self_care: "Perawatan mandiri",
};

export default function KeluhanPage() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState<SymptomAssessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (name: keyof typeof form, value: string) => setForm((current) => ({ ...current, [name]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (form.complaint.trim().length < 10) {
      setError("Ceritakan keluhan sedikit lebih lengkap.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await assessSymptoms({ ...form, age: form.age ? Number(form.age) : null }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Keluhan belum dapat dianalisis");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="symptom-shell">
      <nav className="site-nav"><div className="nav-inner"><a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a><div className="nav-links"><a href="/drugs">Database Obat</a><a href="/interactions">Interaksi</a><a href="/keluhan" className="symptom-nav-active">Cerita Keluhan</a><a href="/ocr">Resep</a></div><a href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></a></div></nav>
      <section className="symptom-page">
        <header className="symptom-heading"><span className="section-kicker">PHARMAI CARE</span><h1>Ceritakan keluhanmu,<br /><em>temukan langkah yang aman.</em></h1><p>Jawaban membantu triase dan perawatan mandiri untuk keluhan ringan—bukan diagnosis atau resep dokter.</p></header>
        <div className="symptom-layout">
          <form className="symptom-form" onSubmit={submit}>
            <label className="symptom-wide"><span>Apa yang Anda rasakan?</span><textarea value={form.complaint} onChange={(e) => update("complaint", e.target.value)} placeholder="Contoh: Sejak tadi pagi kepala terasa pusing dan mual, tetapi tidak muntah..." rows={6} maxLength={3000} required /></label>
            <div className="symptom-fields">
              <label><span>Usia</span><input type="number" min="0" max="120" value={form.age} onChange={(e) => update("age", e.target.value)} placeholder="Contoh: 25" /></label>
              <label><span>Jenis kelamin</span><select value={form.sex} onChange={(e) => update("sex", e.target.value)}><option value="">Pilih</option><option>Laki-laki</option><option>Perempuan</option><option value="tidak ingin menyebutkan">Tidak ingin menyebutkan</option></select></label>
              <label><span>Sudah berapa lama?</span><input value={form.duration} onChange={(e) => update("duration", e.target.value)} placeholder="Contoh: 2 hari" /></label>
              <label><span>Hamil/menyusui</span><select value={form.pregnancy_status} onChange={(e) => update("pregnancy_status", e.target.value)}><option value="">Tidak relevan/tidak disebutkan</option><option>Tidak</option><option>Hamil</option><option>Menyusui</option><option>Mungkin hamil</option></select></label>
            </div>
            <label className="symptom-wide"><span>Penyakit atau kondisi yang dimiliki</span><input value={form.existing_conditions} onChange={(e) => update("existing_conditions", e.target.value)} placeholder="Contoh: maag, hipertensi, asma" /></label>
            <label className="symptom-wide"><span>Obat yang sedang dikonsumsi</span><input value={form.current_medicines} onChange={(e) => update("current_medicines", e.target.value)} placeholder="Tuliskan nama obat dan dosis bila diketahui" /></label>
            <label className="symptom-wide"><span>Alergi obat</span><input value={form.allergies} onChange={(e) => update("allergies", e.target.value)} placeholder="Contoh: alergi ibuprofen; atau tidak ada" /></label>
            <div className="symptom-consent"><b>Privasi</b><p>Keluhan dikirim ke penyedia AI untuk dianalisis dan tidak disimpan oleh fitur ini. Jangan masukkan nama lengkap, alamat, atau identitas lain.</p></div>
            {error && <div className="symptom-error">{error}</div>}
            <button className="primary-action symptom-submit" type="submit" disabled={loading}>{loading ? "Menganalisis keluhan…" : "Lihat langkah yang aman"}<span aria-hidden="true">→</span></button>
          </form>

          <aside className="symptom-result">
            {!result && !loading && <div className="symptom-placeholder"><span>✦</span><h2>Hasil akan tampil di sini.</h2><p>Lengkapi informasi agar saran lebih aman dan relevan.</p></div>}
            {loading && <div className="symptom-placeholder"><span className="spinner" /><h2>Sedang menelaah keluhan…</h2></div>}
            {result && <div className={`symptom-answer urgency-${result.urgency}`}>
              <div className="urgency-banner"><small>TINGKAT TINDAKAN</small><strong>{urgencyLabel[result.urgency] || result.urgency}</strong></div>
              <section><h2>Ringkasan</h2><p>{result.assessment}</p></section>
              {result.red_flags?.length > 0 && <section className="red-flag-box"><h2>Tanda bahaya</h2><ul>{result.red_flags.map((item, index) => <li key={index}>{item}</li>)}</ul></section>}
              {result.self_care?.length > 0 && <section><h2>Yang dapat dilakukan sekarang</h2><ul>{result.self_care.map((item, index) => <li key={index}>{item}</li>)}</ul></section>}
              {result.otc_options?.length > 0 && <section><h2>Opsi obat bebas</h2><div className="otc-list">{result.otc_options.map((option, index) => <article key={index}><strong>{option.medicine}</strong><p>{option.purpose}</p><small>{option.directions}</small><em>{option.cautions}</em></article>)}</div></section>}
              {result.next_steps?.length > 0 && <section><h2>Langkah berikutnya</h2><ul>{result.next_steps.map((item, index) => <li key={index}>{item}</li>)}</ul></section>}
              <p className="symptom-disclaimer">{result.disclaimer || "Hasil AI bukan diagnosis atau resep."}</p>
            </div>}
          </aside>
        </div>
      </section>
    </main>
  );
}
