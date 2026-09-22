"use client";

import { fetchDrug, type Drug } from "@/lib/api";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function DrugDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [drug, setDrug] = useState<Drug | null>(null);
  const [error, setError] = useState(false);
  const statusLabel: Record<string, string> = {
    active: "Izin aktif",
    expired: "Izin kedaluwarsa",
    revoked: "Izin dicabut",
    not_found: "Tidak ditemukan",
    unverified: "Belum diverifikasi",
  };

  useEffect(() => {
    fetchDrug(Number(id)).then(setDrug).catch(() => setError(true));
  }, [id]);

  return (
    <main className="drugs-shell">
      <nav className="site-nav"><div className="nav-inner"><Link href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></Link><div className="nav-links"><Link href="/drugs" className="drugs-nav-active">Database Obat</Link><Link href="/interactions">Interaksi</Link><Link href="/ocr">Resep</Link></div><Link href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></Link></div></nav>

      <section className="drug-detail-page">
        <Link href="/drugs" className="detail-back">← Kembali ke database</Link>
        {error ? (
          <div className="empty-drugs"><h1>Obat tidak ditemukan</h1><p>Data mungkin telah dipindahkan atau dihapus.</p><Link href="/drugs" className="primary-action">Lihat database</Link></div>
        ) : !drug ? (
          <div className="drug-detail-loading"><div /><div /><div /></div>
        ) : (
          <article className="drug-detail">
            <header className="drug-detail-hero">
              <div className={`drug-detail-avatar ${drug.image_url ? "has-image" : ""}`}>{drug.image_url ? <img src={drug.image_url} alt={drug.name} /> : <span>{drug.name.charAt(0).toUpperCase()}</span>}</div>
              <div><span className="section-kicker">DETAIL OBAT · ID {String(drug.id).padStart(3, "0")}</span><h1>{drug.name}</h1>{drug.generic_name && <p>{drug.generic_name}</p>}</div>
            </header>

            <div className="drug-detail-content">
              <section><span className="section-kicker">INFORMASI RINGKAS</span><h2>Tentang obat ini</h2><p>{drug.description || "Deskripsi obat belum tersedia."}</p></section>
              <dl>
                <div><dt>Kategori</dt><dd>{drug.category || "Belum tersedia"}</dd></div>
                <div><dt>Bentuk sediaan</dt><dd>{drug.dosage_form || "Belum tersedia"}</dd></div>
                <div><dt>Produsen</dt><dd>{drug.manufacturer || "Belum tersedia"}</dd></div>
                <div><dt>Nama generik</dt><dd>{drug.generic_name || "Belum tersedia"}</dd></div>
                <div><dt>Zat aktif</dt><dd>{drug.active_ingredients?.join(", ") || "Belum tersedia"}</dd></div>
                <div><dt>Nomor izin edar</dt><dd>{drug.registration_number || "Belum tersedia"}</dd></div>
                <div><dt>Status registrasi</dt><dd><span className={`registration-status status-${drug.registration_status}`}>{statusLabel[drug.registration_status] || drug.registration_status}</span></dd></div>
                <div><dt>Berlaku sampai</dt><dd>{drug.registration_expires_at ? new Date(drug.registration_expires_at).toLocaleDateString("id-ID") : "Belum tersedia"}</dd></div>
              </dl>
            </div>

            <section className="regulatory-source">
              <div><span className="section-kicker">VERIFIKASI REGULASI</span><h2>Sumber pemeriksaan BPOM</h2><p>{drug.regulatory_notes || "Produk ini belum diverifikasi terhadap data registrasi resmi BPOM."}</p>{drug.regulatory_checked_at && <small>Terakhir diperiksa {new Date(drug.regulatory_checked_at).toLocaleString("id-ID")}</small>}</div>
              <a href={drug.regulatory_source_url || "https://cekbpom.pom.go.id/"} target="_blank" rel="noreferrer" className="primary-action">Cek di BPOM <span aria-hidden="true">↗</span></a>
            </section>

            <aside className="drug-detail-note"><strong>Gunakan sebagai referensi informasi.</strong><p>Informasi ini bukan pengganti diagnosis, resep, atau konsultasi dari dokter dan apoteker.</p></aside>
          </article>
        )}
      </section>
    </main>
  );
}
