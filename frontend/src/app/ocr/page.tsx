"use client";

import { useRef, useState } from "react";

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  duration: string;
}

interface PrescriptionResult {
  patient_name?: string;
  doctor_name?: string;
  medications: Medication[];
  notes?: string;
  raw_text?: string;
}

export default function OCRPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<PrescriptionResult | null>(null);
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
      formData.append("file", blob, "prescription.jpg");

      const res = await fetch("/api/ai/ocr-prescription", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Gagal membaca resep");
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ raw_text: "Gagal membaca resep. Coba lagi.", medications: [] });
    } finally {
      setScanning(false);
    }
  };

  const handleReset = () => {
    setPreview(null);
    setResult(null);
  };

  return (
    <main className="ocr-shell">
      <nav className="site-nav"><div className="nav-inner"><a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a><div className="nav-links"><a href="/drugs">Database Obat</a><a href="/interactions">Interaksi</a><a href="/ocr" className="ocr-nav-active">Resep</a></div><a href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></a></div></nav>
      <section className="ocr-page">
        <div className="ocr-heading"><div><span className="section-kicker">PHARMAI READ</span><h1>Baca resep,<br /><em>lebih sederhana.</em></h1><p>Ubah tulisan resep dokter menjadi informasi yang lebih terstruktur dan mudah dipahami.</p></div><div className="ocr-step"><span>01</span><div><strong>UNGGAH RESEP</strong><small>Foto JPG, PNG hingga 10 MB</small></div></div></div>
        {!preview ? <div className="ocr-workspace"><div onDrop={handleDrop} onDragOver={(e) => e.preventDefault()} onClick={openFilePicker} className="ocr-upload" role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") openFilePicker(); }}><div className="ocr-paper-icon"><span>≡</span></div><span className="upload-kicker">MULAI DARI SINI</span><h2>Letakkan foto resep Anda<br /><em>di area ini.</em></h2><p>Seret & lepas foto, atau pilih dari perangkat Anda.</p><div className="upload-actions"><button onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }} className="primary-action">Pilih dari perangkat <span aria-hidden="true">↗</span></button><button onClick={(e) => { e.stopPropagation(); cameraInputRef.current?.click(); }} className="camera-action"><span aria-hidden="true">◎</span> Buka kamera</button></div><div className="upload-meta"><span>⌁</span> Pastikan seluruh resep terlihat di dalam bingkai</div><input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileChange} className="hidden" /><input ref={cameraInputRef} type="file" accept="image/*" capture="environment" onChange={handleFileChange} className="hidden" /></div><aside className="ocr-tips"><span className="section-kicker">TIPS FOTO RESEP</span><h3>Tulisan yang jelas membantu AI membaca lebih baik.</h3><div className="tip-list"><div><span>01</span><p>Foto resep dari atas, jangan miring.</p></div><div><span>02</span><p>Gunakan pencahayaan merata tanpa silau.</p></div><div><span>03</span><p>Pastikan tulisan tidak terpotong.</p></div></div></aside></div> : <div className="ocr-workspace ocr-preview-workspace"><div className="ocr-preview-panel"><div className="preview-label"><span>RESEP SIAP DIBACA</span><button onClick={handleReset} aria-label="Hapus foto">✕</button></div><img src={preview} alt="Preview resep" /></div><div className="ocr-result-column">{!result && <div className="ocr-ready"><span className="section-kicker">LANGKAH BERIKUTNYA</span><h2>Resep Anda sudah siap.</h2><p>PharmAI akan mengenali identitas, obat, dosis, dan instruksi yang tertulis.</p><button onClick={handleScan} disabled={scanning} className="primary-action scan-submit">{scanning ? "Membaca resep..." : "Mulai baca dengan AI"}<span aria-hidden="true">→</span></button><button onClick={handleReset} className="reset-action">Pilih foto lain</button></div>}{result && <div className="ocr-result-card"><div className="result-card-top"><span className="section-kicker">TRANSKRIP RESEP</span><span className="ocr-count">{result.medications.length.toString().padStart(2, "0")} OBAT</span></div>{(result.patient_name || result.doctor_name) && <div className="prescription-meta">{result.patient_name && <span><b>PASIEN</b>{result.patient_name}</span>}{result.doctor_name && <span><b>DOKTER</b>{result.doctor_name}</span>}</div>}{result.medications.length > 0 && <div className="medication-list"><h3>Daftar obat</h3>{result.medications.map((med, i) => <div className="medication-row" key={i}><span className="medication-index">0{i + 1}</span><div><strong>{med.name}</strong><p>{med.dosage} <span>·</span> {med.frequency} <span>·</span> {med.duration}</p></div></div>)}</div>}{result.notes && <div className="ocr-note"><b>CATATAN</b><p>{result.notes}</p></div>}{result.raw_text && <div className="raw-prescription"><b>TRANSKRIP MENTAH</b><p>{result.raw_text}</p></div>}<button onClick={handleReset} className="reset-action">Baca resep lain</button></div>}</div></div>}
      </section>
    </main>
  );
}
