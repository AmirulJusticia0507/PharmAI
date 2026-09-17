"use client";

import { useEffect, useState } from "react";
import { fetchDrugs, type Drug } from "@/lib/api";

export default function DrugsPage() {
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDrugs = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDrugs({ search: q, limit: 50 });
      setDrugs(data);
    } catch {
      setError("Gagal mengambil data obat");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDrugs();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadDrugs(search);
  };

  return (
    <main className="min-h-screen">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="/" className="text-xl font-bold text-blue-600">
            PharmAI
          </a>
          <div className="flex gap-4 text-sm">
            <a href="/drugs" className="text-blue-600 font-medium">
              Obat
            </a>
            <a href="/scan" className="hover:text-blue-600">
              Scan Pil
            </a>
            <a href="/interactions" className="hover:text-blue-600">
              Interaksi
            </a>
          </div>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Database Obat</h1>

        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Cari obat berdasarkan nama..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Cari
          </button>
        </form>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 text-gray-500">Memuat data...</div>
        ) : drugs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            {search
              ? `Tidak ada obat ditemukan untuk "${search}"`
              : "Belum ada data obat"}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {drugs.map((drug) => (
              <DrugCard key={drug.id} drug={drug} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function DrugCard({ drug }: { drug: Drug }) {
  return (
    <div className="bg-white p-5 rounded-xl shadow-sm border hover:shadow-md transition">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-lg">{drug.name}</h3>
        {drug.category && (
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
            {drug.category}
          </span>
        )}
      </div>
      {drug.generic_name && (
        <p className="text-sm text-gray-500 mb-1">Generik: {drug.generic_name}</p>
      )}
      {drug.dosage_form && (
        <p className="text-sm text-gray-500 mb-1">Bentuk: {drug.dosage_form}</p>
      )}
      {drug.manufacturer && (
        <p className="text-sm text-gray-500 mb-2">
          Produsen: {drug.manufacturer}
        </p>
      )}
      {drug.description && (
        <p className="text-sm text-gray-600 line-clamp-2">{drug.description}</p>
      )}
    </div>
  );
}
