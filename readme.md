# PharmAI — Rangkuman Sistem & Fitur AI Analisis Obat

Dokumen ini memuat rangkuman penerapan Artificial Intelligence (AI) dalam analisis obat, mencakup kategori konsumen, riset farmasi, aplikasi populer di pasaran, serta opsi *Open Source* untuk pengembang.

---

## 1. Klasifikasi AI dalam Bidang Obat-obatan

AI untuk analisis obat terbagi menjadi dua ranah utama:

*   **Aplikasi Konsumen (Sehari-hari):**
    *   **Pill Visual Identification** — Memindai foto fisik pil/kapsul (bentuk, warna, imprint).
    *   **Prescription OCR Scanner** — Membaca dan mentranskrip tulisan tangan resep dokter.
    *   **Interaction Checker** — Menganalisis potensi kontradiksi atau efek samping jika beberapa obat dikonsumsi bersamaan.
*   **Riset Farmasi & Lab (Drug Discovery):**
    *   **Virtual Molecular Screening** — Simulasi jutaan struktur kimia untuk menemukan kandidat obat.
    *   **Toxicity & Efficacy Prediction** — Memprediksi keamanan dan efektivitas senyawa sebelum uji klinis.
    *   **Herbal Compounds Analysis** — Pemodelan senyawa aktif tanaman obat tradisional (kunyit, temulawak, dll.).

---

## 2. Matriks Aplikasi & Fitur AI

| Aplikasi / Proyek | Lisensi | Target | Fitur Utama | Teknologi |
| :--- | :--- | :--- | :--- | :--- |
| **AI Pill ID** | Freemium | Pasien | Scan pil lepas via kamera, cek interaksi obat, basis data dosis & efek samping | Computer Vision |
| **PillLens / Smart Pill ID** | Freemium | Pasien | Scan bentuk obat dan pemindaian label kemasan | Computer Vision |
| **Drugs.com Identifier** | Gratis (Web/App) | Pasien & Medis | Pencarian & pencocokan manual/foto berdasarkan kode fisik (*imprint*) | Database Matching |
| **MediScribe AI** | Open Source (MIT) | Developer | OCR tulisan tangan resep dokter menjadi teks digital | Handwritten OCR / VLM |
| **PillSearch (YOLOv8)** | Open Source | Developer | Deteksi dan pemisahan objek pil dari foto | YOLOv8, FastSAM |
| **PrescriptoAI / Rx-OCR** | API (Pay-as-you-go) | Integrasi Dev | API pembacaan resep fisik untuk sistem informasi apotek | OCR API |

---

## 3. Ringkasan Fitur AI

| Fitur | Deskripsi | Teknologi |
| :--- | :--- | :--- |
| **Scan Fisik Pil & Kapsul** | Pemeriksaan warna, bentuk, dan tulisan timbul pada pil | Computer Vision (YOLOv8, FastSAM) |
| **Transkrip Resep Dokter** | Membaca tulisan tangan di resep kertas | Handwritten OCR / Vision Language Models |
| **Deteksi Interaksi Obat** | Penilaian keamanan kombinasi bahan aktif | NLP & Knowledge Graphs |
| **Prediksi Penemuan Obat** | Simulasi penempelan molekul pada target protein | Deep Learning, Molecular Docking |

---

## 4. Catatan Batasan & Keselamatan

1.  **Akurasi Visual** — Pemindaian AI dapat terkecoh oleh dua obat berbeda dengan ukuran, bentuk, dan warna yang persis sama.
2.  **Verifikasi Medis** — Hasil analisis aplikasi konsumen tidak menggantikan keputusan medis profesional. Konfirmasi apoteker atau dokter tetap wajib sebelum mengonsumsi obat.

---

*Dokumen dirangkum untuk referensi teknis dan umum.*
