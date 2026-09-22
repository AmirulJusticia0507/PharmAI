"use client";

import { fetchDrugCount, fetchDrugs, type Drug } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";

const PAGE_SIZE = 10;

export default function DrugsPage() {
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [totalDrugs, setTotalDrugs] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDrugs = async (q?: string) => {
    setLoading(true);
    setError(null);
    try {
      const [data, total] = await Promise.all([
        fetchDrugs({ search: q, limit: 100 }),
        fetchDrugCount(),
      ]);
      setDrugs(data);
      setTotalDrugs(total);
      setPage(1);
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

  const totalPages = Math.ceil(drugs.length / PAGE_SIZE);
  const visibleDrugs = drugs.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

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
        <div className="catalog-toolbar"><span><strong>{loading ? "Memuat" : drugs.length}</strong> ditampilkan dari <strong>{totalDrugs.toLocaleString("id-ID")}</strong> obat</span><span className="catalog-note"><i /> Informasi untuk referensi, bukan pengganti konsultasi medis</span></div>

        {error && <div className="drugs-error"><strong>Data belum dapat dimuat.</strong><span>{error}</span><button onClick={() => loadDrugs(search)}>Coba lagi</button></div>}
        {loading ? <div className="drug-grid"><div className="drug-skeleton" /><div className="drug-skeleton" /><div className="drug-skeleton" /></div> : drugs.length === 0 ? <div className="empty-drugs"><span>⌁</span><h2>{search ? `Tidak ada obat untuk "${search}"` : "Belum ada data obat"}</h2><p>Coba kata kunci lain atau mulai dengan memindai obat.</p><a href="/scan" className="primary-action">Scan obat <span aria-hidden="true">↗</span></a></div> : <><div className="drug-grid">{visibleDrugs.map((drug) => <DrugCard key={drug.id} drug={drug} />)}</div><nav className="drug-pagination" aria-label="Navigasi halaman obat"><button type="button" onClick={() => setPage(page - 1)} disabled={page === 1} aria-label="Halaman sebelumnya">←</button>{Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => <button type="button" key={number} onClick={() => setPage(number)} className={number === page ? "active" : ""} aria-current={number === page ? "page" : undefined}>{number}</button>)}<button type="button" onClick={() => setPage(page + 1)} disabled={page === totalPages} aria-label="Halaman berikutnya">→</button></nav></>}
      </section>
    </main>
  );
}

function DrugCard({ drug }: { drug: Drug }) {
  return (
    <Link href={`/drugs/${drug.id}`} className="drug-card" aria-label={`Lihat detail ${drug.name}`}>
      <div className="drug-card-top"><div className={`drug-avatar ${drug.image_url ? "has-image" : ""}`}>{drug.image_url ? <img src={drug.image_url} alt="" /> : <span>{drug.name.charAt(0).toUpperCase()}</span>}</div>{drug.category && <span className="drug-category">{drug.category}</span>}</div>
      <h2>{drug.name}</h2>
      {drug.generic_name && <p className="drug-generic">{drug.generic_name}</p>}
      <div className="drug-details">{drug.dosage_form && <span><b>BENTUK</b>{drug.dosage_form}</span>}{drug.manufacturer && <span><b>PRODUSEN</b>{drug.manufacturer}</span>}</div>
      {drug.description && <p className="drug-description">{drug.description}</p>}
      <div className="drug-card-footer"><span>ID {String(drug.id).padStart(3, "0")}</span><span className="drug-card-mark" aria-hidden="true">✦</span></div>
    </Link>
  );
}
