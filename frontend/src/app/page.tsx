export default function Home() {
  return (
    <main className="pharma-shell">
      <nav className="site-nav">
        <div className="nav-inner">
          <a href="/" className="brand" aria-label="PharmAI beranda"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></a>
          <div className="nav-links"><a href="/drugs">Database Obat</a><a href="/interactions">Interaksi</a><a href="/ocr">Resep</a></div>
          <a href="/scan" className="nav-action">Mulai scan <span aria-hidden="true">↗</span></a>
        </div>
      </nav>

      <section className="hero-section">
        <div className="hero-copy">
          <div className="eyebrow"><span className="pulse-dot" /> Asisten kesehatan digital Anda</div>
          <h1>Kenali obat.<br /><em>Jaga kesehatan.</em></h1>
          <p className="hero-description">PharmAI membantu Anda memahami obat, membaca resep, dan menemukan potensi interaksi dengan lebih cepat dan tenang.</p>
          <div className="hero-actions"><a href="/scan" className="primary-action">Scan obat sekarang <span aria-hidden="true">→</span></a><a href="/drugs" className="text-action">Jelajahi database <span aria-hidden="true">↗</span></a></div>
          <div className="trust-line"><span className="trust-avatars"><i /><i /><i /></span> Dipakai untuk keputusan yang lebih aman</div>
        </div>
        <div className="hero-visual">
          <div className="visual-glow" />
          <div className="scan-card">
            <div className="scan-card-top"><span>ANALISIS TERKINI</span><span className="live-status">● LIVE</span></div>
            <div className="medicine-photo"><img src="https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=900&q=85" alt="Kapsul dan obat di atas meja" /></div>
            <div className="scan-result"><div><span className="result-label">HASIL IDENTIFIKASI</span><strong>Amoxicillin 500 mg</strong></div><span className="confidence">98%</span></div>
            <div className="result-bar"><span /></div>
          </div>
          <div className="floating-note note-top"><span className="note-icon">✓</span><div><strong>Aman digunakan</strong><small>Analisis selesai</small></div></div>
          <div className="floating-note note-bottom"><span className="note-icon blue">⌁</span><div><strong>3 fitur pintar</strong><small>Dalam satu platform</small></div></div>
        </div>
      </section>

      <section className="feature-section">
        <div className="section-heading"><span className="section-kicker">SATU PLATFORM, LEBIH TENANG</span><h2>Yang Anda butuhkan<br /><span>untuk memahami obat.</span></h2></div>
        <div className="feature-grid">
          <a href="/scan" className="feature-card feature-blue"><span className="feature-icon">⌕</span><span className="card-number">01</span><h3>Identifikasi obat</h3><p>Kenali berbagai bentuk sediaan obat dan kemasannya dengan analisis visual AI.</p><span className="card-arrow">↗</span></a>
          <a href="/interactions" className="feature-card feature-lime"><span className="feature-icon">◌</span><span className="card-number">02</span><h3>Cek interaksi</h3><p>Periksa kombinasi obat dan pahami hal penting sebelum dikonsumsi.</p><span className="card-arrow">↗</span></a>
          <a href="/ocr" className="feature-card feature-white"><span className="feature-icon">≡</span><span className="card-number">03</span><h3>Transkrip resep</h3><p>Ubah tulisan resep dokter menjadi informasi yang lebih mudah dibaca.</p><span className="card-arrow">↗</span></a>
        </div>
      </section>

      <footer className="site-footer"><div className="brand"><span className="brand-mark">+</span><span>Pharm<span>AI</span></span></div><span>Teknologi untuk keputusan kesehatan yang lebih baik.</span><div className="footer-links"><a href="/about">Tentang</a><a href="/help">Bantuan</a><a href="/privacy">Privasi</a><a href="/cookies">Cookies</a><span>© 2025 PharmAI</span></div></footer>
    </main>
  );
}
