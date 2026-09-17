# PharmAI — AI Analisis Obat

Platform analisis obat berbasis AI dengan frontend Next.js, backend FastAPI, dan database PostgreSQL.

---

## Tech Stack

| Layer | Teknologi |
| :--- | :--- |
| Frontend | Next.js 15 (App Router, TypeScript, Tailwind CSS) |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL |
| Deploy | Vercel (Frontend) + Railway/Fly.io (Backend) |

---

## Struktur Proyek

```
PharmAI/
├── frontend/             # Next.js app
│   ├── src/app/          # App Router pages
│   ├── src/components/   # Reusable components
│   ├── src/lib/          # API client & utilities
│   └── package.json
├── backend/              # FastAPI app
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── database.py   # DB connection
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── routes/       # API routes
│   └── requirements.txt
├── vercel.json           # Vercel deploy config
└── .gitignore
```

---

## Setup Lokal

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:3000`

### 3. Environment Variables

Buat file `.env` di `backend/`:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pharmaidb
```

Buat file `.env.local` di `frontend/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Deploy ke Vercel

1. Push repo ke GitHub
2. Import repo di [vercel.com/new](https://vercel.com/new)
3. Set **Root Directory** → `frontend`
4. Set env var `NEXT_PUBLIC_API_URL` → URL backend production
5. Deploy

Backend deploy terpisah di Railway/Fly.io, lalu hubungkan URL-nya ke env var Vercel.

---

## API Endpoints

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| GET | `/api/health` | Health check |
| GET | `/api/drugs` | List semua obat (support search & filter) |
| GET | `/api/drugs/{id}` | Detail satu obat |
| POST | `/api/drugs` | Tambah obat baru |
| PUT | `/api/drugs/{id}` | Update obat |
| DELETE | `/api/drugs/{id}` | Hapus obat |

---

## Fitur (Roadmap)

- [ ] Identifikasi pil via foto (Computer Vision)
- [ ] Transkrip resep dokter (OCR)
- [ ] Cek interaksi obat (NLP)
- [ ] Database obat Indonesia
- [ ] Dashboard admin

---

*Dokumen dirangkum untuk referensi teknis dan umum.*
