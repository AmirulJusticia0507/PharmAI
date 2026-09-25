"use client";

import { fetchDrugCount, fetchDrugs, type Drug } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";

const PAGE_SIZE = 10;

export default function DrugsPage() {
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [totalDrugs, setTotalDrugs] = useState(0);
  const [resultCount, setResultCount] = useState(0);
  const [search, setSearch] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDrugs = async (q = "", pageNumber = 1) => {
    setLoading(true);
    setError(null);
    try {
      const [data, total] = await Promise.all([
        fetchDrugs({ search: q, skip: (pageNumber - 1) * PAGE_SIZE, limit: PAGE_SIZE }),
        fetchDrugCount(q),
      ]);
      setDrugs(data);
      setResultCount(total);
      if (!q) setTotalDrugs(total);
      setActiveSearch(q);
      setPage(pageNumber);
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
    loadDrugs(search.trim(), 1);
  };

  const totalPages = Math.max(1, Math.ceil(resultCount / PAGE_SIZE));
  const nearbyPages = Array.from(new Set([page - 1, page, page + 1]))
    .filter((number) => number > 1 && number <= totalPages);
  const goToPage = (pageNumber: number) => loadDrugs(activeSearch, pageNumber);

  return (
    <main className="drugs-shell">
      <nav className="site-nav">
        <div className="nav-inner">
          <a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a>
          <div className="nav-links"><a href="/drugs" className="drugs-nav-active">Database Obat</a><a href="/interactions">Interaksi</a><a href="/ocr">Resep</a></div>
          <a href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></a>
        </div>
      </nav>

      <section className="drugs-page">
        <div className="drugs-heading"><div><span className="section-kicker">PHARMAI LIBRARY</span><h1>Temukan obat,<br /><em>lebih mudah.</em></h1><p>Jelajahi informasi obat yang terkurasi untuk membantu Anda memahami apa yang dikonsumsi.</p></div><div className="library-stamp"><span>DATABASE</span><strong>{loading ? "--" : `${drugs.length.toLocaleString("id-ID")} / ${totalDrugs.toLocaleString("id-ID")}`}</strong><small>ditampilkan / total obat</small></div></div>

        <form onSubmit={handleSearch} className="drug-search"><span className="search-icon" aria-hidden="true">⌕</span><input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Cari nama obat, generik, atau kategori..." aria-label="Cari obat" /><button type="submit">Cari <span aria-hidden="true">→</span></button></form>
        <div className="catalog-toolbar"><span><strong>{loading ? "Memuat" : drugs.length}</strong> ditampilkan dari <strong>{resultCount.toLocaleString("id-ID")}</strong> hasil</span><span className="catalog-note"><i /> Informasi untuk referensi, bukan pengganti konsultasi medis</span></div>

        {error && <div className="drugs-error"><strong>Data belum dapat dimuat.</strong><span>{error}</span><button onClick={() => loadDrugs(search)}>Coba lagi</button></div>}
        {loading ? <div className="drug-grid"><div className="drug-skeleton" /><div className="drug-skeleton" /><div className="drug-skeleton" /></div> : drugs.length === 0 ? <div className="empty-drugs"><span>⌁</span><h2>{activeSearch ? `Tidak ada obat untuk "${activeSearch}"` : "Belum ada data obat"}</h2><p>Coba kata kunci lain atau mulai dengan memindai obat.</p><a href="/scan" className="primary-action">Scan obat <span aria-hidden="true">↗</span></a></div> : <><div className="drug-grid">{drugs.map((drug) => <DrugCard key={drug.id} drug={drug} />)}</div><nav className="drug-pagination" aria-label="Navigasi halaman obat"><button type="button" onClick={() => goToPage(page - 1)} disabled={page === 1 || loading} aria-label="Halaman sebelumnya">←</button><button type="button" onClick={() => goToPage(1)} className={page === 1 ? "active" : ""} aria-current={page === 1 ? "page" : undefined}>1</button>{page > 3 && <span className="pagination-gap">…</span>}{nearbyPages.map((number) => <button type="button" key={number} onClick={() => goToPage(number)} className={number === page ? "active" : ""} aria-current={number === page ? "page" : undefined}>{number}</button>)}<button type="button" onClick={() => goToPage(page + 1)} disabled={page === totalPages || loading} aria-label="Halaman berikutnya">→</button><button type="button" className="pagination-last" onClick={() => goToPage(totalPages)} disabled={page === totalPages || loading}>Last</button></nav></>}
      </section>
    </main>
  );
}

function DrugCard({ drug }: { drug: Drug }) {
  return (
    <Link href={`/drugs/${drug.id}`} className="drug-card" aria-label={`Lihat detail ${drug.name}`}>
      <div className="drug-card-top"><div className={`drug-avatar ${drug.image_url ? "has-image" : ""}`}>{drug.image_url ? <img src={drug.image_url} alt="" /> : <span>{drug.name.charAt(0).toUpperCase()}</span>}</div><div className="drug-card-meta">{drug.category && <span className="drug-category">{drug.category}</span>}<span className="drug-id">ID {String(drug.id).padStart(3, "0")}</span></div></div>
      <h2>{drug.name}</h2>
      {drug.generic_name && <p className="drug-generic">{drug.generic_name}</p>}
      <div className="drug-details">{drug.dosage_form && <span><b>BENTUK</b>{drug.dosage_form}</span>}{drug.frequency && <span><b>FREKUENSI</b>{drug.frequency}</span>}{drug.manufacturer && <span><b>PRODUSEN</b>{drug.manufacturer}</span>}</div>
      {drug.description && <p className="drug-description">{drug.description}</p>}
      <div className="drug-card-footer"><span className="drug-card-mark" aria-hidden="true">✦</span></div>
    </Link>
  );
}
