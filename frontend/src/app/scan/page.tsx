"use client";

import { useRef, useState } from "react";

interface ScanResult {
  name: string;
  dosage: string;
  category: string;
  active_ingredients: string[];
  registration_number: string;
  description: string;
  confidence: number;
}

export default function ScanPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    const url = URL.createObjectURL(file);
    setPreview(url);
    setResult(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  };

  const openFilePicker = () => fileInputRef.current?.click();

  const handleScan = async () => {
    if (!preview) return;
    setScanning(true);
    try {
      const blob = await fetch(preview).then((r) => r.blob());
      const formData = new FormData();
      formData.append("file", blob, "pill.jpg");

      const res = await fetch("/api/ai/scan-pill", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Gagal scan");
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({
        name: "Gagal mengenali",
        dosage: "",
        category: "",
        active_ingredients: [],
        registration_number: "",
        description: "Terjadi kesalahan. Coba foto dengan pencahayaan lebih baik.",
        confidence: 0,
      });
    } finally {
      setScanning(false);
    }
  };

  const handleReset = () => {
    setPreview(null);
    setResult(null);
  };

  return (
    <main className="scan-shell">
      <nav className="site-nav">
        <div className="nav-inner">
          <a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a>
          <div className="nav-links"><a href="/drugs">Database Obat</a><a href="/interactions">Interaksi</a><a href="/ocr">Resep</a></div>
          <a href="/scan" className="nav-action scan-nav-active">Scan pil <span aria-hidden="true">↗</span></a>
        </div>
      </nav>

      <section className="scan-page">
        <div className="scan-heading">
          <div><span className="section-kicker">PHARMAI VISION</span><h1>Identifikasi obat<br /><em>dalam sekejap.</em></h1><p>Ambil foto pil atau kapsul untuk mendapatkan informasi yang lebih jelas, cepat, dan terpercaya.</p></div>
          <div className="scan-step"><span>01</span><div><strong>UNGGAH FOTO</strong><small>Format JPG, PNG hingga 10 MB</small></div></div>
        </div>

        {!preview ? (
          <div className="scan-workspace">
            <div onDrop={handleDrop} onDragOver={(e) => e.preventDefault()} onClick={openFilePicker} className="upload-zone" role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") openFilePicker(); }}>
              <div className="upload-orbit"><span>✦</span></div>
              <span className="upload-kicker">MULAI DARI SINI</span>
              <h2>Letakkan foto pil Anda<br /><em>di area ini.</em></h2>
              <p>Seret & lepas foto, atau pilih dari perangkat Anda.</p>
              <div className="upload-actions">
                <button onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }} className="primary-action">Pilih dari perangkat <span aria-hidden="true">↗</span></button>
                <button onClick={(e) => { e.stopPropagation(); cameraInputRef.current?.click(); }} className="camera-action"><span aria-hidden="true">◎</span> Buka kamera</button>
              </div>
              <div className="upload-meta"><span>⌁</span> Foto dengan pencahayaan baik untuk hasil maksimal</div>
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" onChange={handleFileChange} className="hidden" />
            </div>
            <aside className="scan-tips"><span className="section-kicker">TIPS FOTO TERBAIK</span><h3>Hasil yang lebih akurat dimulai dari foto yang baik.</h3><div className="tip-list"><div><span>01</span><p>Letakkan obat di permukaan yang datar.</p></div><div><span>02</span><p>Pastikan pil terlihat jelas dan tidak buram.</p></div><div><span>03</span><p>Gunakan cahaya alami, hindari bayangan.</p></div></div></aside>
          </div>
        ) : (
          <div className="scan-workspace preview-workspace">
            <div className="preview-panel"><div className="preview-label"><span>FOTO SIAP DIANALISIS</span><button onClick={handleReset} aria-label="Hapus foto">✕</button></div><img src={preview} alt="Preview pil" /></div>
            <div className="result-column">
              {!result && <div className="scan-ready"><span className="section-kicker">LANGKAH BERIKUTNYA</span><h2>Foto Anda sudah siap.</h2><p>Biarkan PharmAI membaca bentuk, warna, dan karakteristik obat ini.</p><button onClick={handleScan} disabled={scanning} className="primary-action scan-submit">{scanning ? "Memindai dengan AI..." : "Mulai analisis AI"}<span aria-hidden="true">→</span></button><button onClick={handleReset} className="reset-action">Pilih foto lain</button></div>}
              {result && <div className="result-card"><div className="result-card-top"><span className="section-kicker">HASIL IDENTIFIKASI</span>{result.confidence > 0 && <span className="confidence-badge">{Math.round(result.confidence * 100)}% yakin</span>}</div><h2>{result.name}</h2>{result.dosage && <div className="result-line"><span>DOSIS</span><strong>{result.dosage}</strong></div>}{result.category && <div className="result-line"><span>KATEGORI</span><strong>{result.category}</strong></div>}{result.active_ingredients?.length > 0 && <div className="result-line"><span>ZAT AKTIF</span><strong>{result.active_ingredients.join(", ")}</strong></div>}{result.registration_number && <div className="result-line"><span>NOMOR IZIN TERBACA</span><strong>{result.registration_number}</strong></div>}<p>{result.description}</p><small className="scan-verification-note">Identifikasi gambar belum membuktikan izin edar. Cocokkan nomor dan komposisi dengan sumber resmi BPOM.</small><div className="result-actions"><button onClick={handleReset} className="reset-action">Scan lagi</button><a href="/drugs" className="primary-action">Lihat database <span aria-hidden="true">↗</span></a></div></div>}
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
