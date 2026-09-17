export default function Home() {
  return (
    <main className="min-h-screen">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-600">PharmAI</h1>
          <div className="flex gap-4 text-sm">
            <a href="/drugs" className="hover:text-blue-600">Obat</a>
            <a href="/scan" className="hover:text-blue-600">Scan Pil</a>
            <a href="/interactions" className="hover:text-blue-600">Interaksi</a>
            <a href="/ocr" className="hover:text-blue-600">Resep</a>
          </div>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-4xl font-bold mb-4">AI Analisis Obat</h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-8">
          Platform untuk identifikasi obat, deteksi interaksi, dan analisis
          berbasis kecerdasan buatan.
        </p>
        <div className="flex justify-center gap-4">
          <a
            href="/scan"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Mulai Scan
          </a>
          <a
            href="/drugs"
            className="border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-100 transition"
          >
            Lihat Database
          </a>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="Identifikasi Pil"
            desc="Scan foto pil/kapsul untuk identifikasi otomatis."
          />
          <FeatureCard
            title="Cek Interaksi Obat"
            desc="Pastikan keamanan kombinasi obat yang dikonsumsi."
          />
          <FeatureCard
            title="Transkrip Resep"
            desc="OCR untuk membaca tulisan tangan resep dokter."
          />
        </div>
      </section>
    </main>
  );
}

function FeatureCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border hover:shadow-md transition">
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{desc}</p>
    </div>
  );
}
