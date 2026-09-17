"use client";

import { useRef, useState } from "react";

interface ScanResult {
  name: string;
  confidence: number;
  description: string;
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
    if (file && file.type.startsWith("image/")) {
      handleFile(file);
    }
  };

  const handleScan = async () => {
    if (!preview) return;
    setScanning(true);
    // Simulasi scan - nanti diganti dengan API callจริง
    await new Promise((r) => setTimeout(r, 2000));
    setResult({
      name: "Paracetamol 500mg",
      confidence: 0.94,
      description:
        "Obat penurun panas dan pereda nyeri. Biasa digunakan untuk sakit kepala, demam, dan nyeri ringan.",
    });
    setScanning(false);
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
            <a href="/scan" className="text-blue-600 font-medium">
              Scan Pil
            </a>
            <a href="/interactions" className="hover:text-blue-600">
              Interaksi
            </a>
          </div>
        </div>
      </nav>

      <section className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">Scan Pil / Kapsul</h1>
        <p className="text-gray-600 mb-6">
          Unggah foto pil atau kapsul untuk identifikasi otomatis.
        </p>

        {!preview ? (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 transition cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="text-4xl mb-4">📷</div>
            <p className="text-gray-600 mb-2">
              Seret & lepas foto di sini
            </p>
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
                alt="Preview pil"
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
                {scanning ? "Memindai..." : "Mulai Scan"}
              </button>
            )}

            {result && (
              <div className="bg-white border rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-lg">{result.name}</h3>
                  <span className="text-sm bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    {Math.round(result.confidence * 100)}% yakin
                  </span>
                </div>
                <p className="text-gray-600 text-sm">{result.description}</p>
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={handleReset}
                    className="flex-1 border border-gray-300 py-2 rounded-lg text-sm hover:bg-gray-100 transition"
                  >
                    Scan Lagi
                  </button>
                  <a
                    href="/drugs"
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm text-center hover:bg-blue-700 transition"
                  >
                    Lihat Database
                  </a>
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
