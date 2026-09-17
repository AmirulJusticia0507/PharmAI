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
            <a href="/interactions" className="hover:text-blue-600">
              Interaksi
            </a>
            <a href="/ocr" className="text-blue-600 font-medium">
              Resep
            </a>
          </div>
        </div>
      </nav>

      <section className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">OCR Resep Dokter</h1>
        <p className="text-gray-600 mb-6">
          Unggah foto resep dokter untuk ditranskrip secara otomatis.
        </p>

        {!preview ? (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 transition cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="text-4xl mb-4">📋</div>
            <p className="text-gray-600 mb-2">Seret & lepas foto resep di sini</p>
            <p className="text-sm text-gray-400 mb-4">atau klik untuk memilih</p>
            <div className="flex justify-center gap-3">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition"
              >
                Pilih File
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  cameraInputRef.current?.click();
                }}
                className="border border-gray-300 px-4 py-2 rounded-lg text-sm hover:bg-gray-100 transition"
              >
                Ambil Foto
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={preview}
                alt="Preview resep"
                className="w-full h-64 object-contain bg-gray-100 rounded-xl"
              />
              <button
                onClick={handleReset}
                className="absolute top-2 right-2 bg-white/80 backdrop-blur text-gray-600 w-8 h-8 rounded-full hover:bg-white transition"
              >
                ✕
              </button>
            </div>

            {!result && (
              <button
                onClick={handleScan}
                disabled={scanning}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:bg-blue-400"
              >
                {scanning ? "Membaca Resep..." : "Baca Resep"}
              </button>
            )}

            {result && (
              <div className="bg-white border rounded-xl p-5 space-y-4">
                {result.patient_name && (
                  <div>
                    <span className="text-sm text-gray-500">Pasien:</span>
                    <p className="font-medium">{result.patient_name}</p>
                  </div>
                )}
                {result.doctor_name && (
                  <div>
                    <span className="text-sm text-gray-500">Dokter:</span>
                    <p className="font-medium">{result.doctor_name}</p>
                  </div>
                )}

                {result.medications.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">Obat:</h3>
                    <div className="space-y-2">
                      {result.medications.map((med, i) => (
                        <div key={i} className="bg-gray-50 p-3 rounded-lg">
                          <p className="font-medium">{med.name}</p>
                          <p className="text-sm text-gray-600">
                            {med.dosage} | {med.frequency} | {med.duration}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.notes && (
                  <div>
                    <span className="text-sm text-gray-500">Catatan:</span>
                    <p className="text-sm">{result.notes}</p>
                  </div>
                )}

                {result.raw_text && (
                  <div>
                    <span className="text-sm text-gray-500">Raw text:</span>
                    <p className="text-sm bg-gray-50 p-3 rounded-lg whitespace-pre-wrap">
                      {result.raw_text}
                    </p>
                  </div>
                )}

                <button
                  onClick={handleReset}
                  className="w-full border border-gray-300 py-2 rounded-lg text-sm hover:bg-gray-100 transition"
                >
                  Scan Lagi
                </button>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
