from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

try:
    from dotenv import load_dotenv
    from pathlib import Path
    _env_backend = Path(__file__).resolve().parent.parent / "backend"
    load_dotenv(_env_backend / ".env")
    load_dotenv(_env_backend / ".env.local", override=True)
except ImportError:
    pass

import httpx
import base64
import json

app = FastAPI(title="PharmAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")
OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "")
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4o-mini")


async def chat_completion(messages: list[dict], model: str | None = None) -> str:
    if OPENROUTER_API_KEY:
        base_url, api_key = OPENROUTER_BASE_URL, OPENROUTER_API_KEY
    elif OMNIROUTE_BASE_URL:
        base_url, api_key = OMNIROUTE_BASE_URL, OMNIROUTE_API_KEY
    else:
        raise HTTPException(status_code=503, detail="Provider AI belum dikonfigurasi")

    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://pharm-ai-rouge.vercel.app",
                "X-Title": "PharmAI",
            },
            json={"model": model or AI_MODEL, "messages": messages, "max_tokens": 1024},
        )
        if not resp.is_success:
            try:
                message = resp.json().get("error", {}).get("message")
            except Exception:
                message = None
            raise HTTPException(
                status_code=502,
                detail=f"Provider AI gagal (HTTP {resp.status_code}){f': {message}' if message else ''}",
            )
        return resp.json()["choices"][0]["message"]["content"]


def parse_json_response(text: str):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(cleaned)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "PharmAI API is running"}


@app.post("/api/ai/scan-pill")
async def scan_pill(file: UploadFile = File(...)):
    contents = await file.read()
    mime = file.content_type or "image/jpeg"
    b64 = base64.b64encode(contents).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Analisis foto obat atau kemasannya, termasuk tablet, kaplet, kapsul, cairan, "
                    "sirup, suspensi, tetes, salep, krim, gel, inhaler, injeksi, suppositoria, atau patch. "
                    "Kembalikan JSON: "
                    '{"name":"nama obat","dosage":"dosis","dosage_form":"bentuk sediaan",'
                    '"category":"kategori dalam Bahasa Indonesia",'
                    '"active_ingredients":["nama zat aktif"],'
                    '"registration_number":"nomor yang terlihat pada kemasan atau kosong",'
                    '"description":"deskripsi singkat dalam Bahasa Indonesia","confidence":0.0-1.0}. '
                    "Pertahankan nama obat, dosis, dan zat aktif sebagaimana tertulis. Jangan mengarang "
                    "kandungan atau nomor izin edar. Jika tidak terlihat jelas, gunakan nilai kosong dan "
                    "confidence rendah. Utamakan tulisan pada kemasan; jangan mengenali obat cair atau "
                    "topikal hanya dari warna dan bentuk wadah. Hanya kembalikan JSON valid."
                )},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }
    ]
    result = await chat_completion(messages)
    try:
        return parse_json_response(result)
    except Exception:
        return {
            "name": "Tidak teridentifikasi", "description": result, "dosage_form": "",
            "active_ingredients": [], "registration_number": "", "confidence": 0.0,
        }


@app.post("/api/ai/ocr-prescription")
async def ocr_prescription(file: UploadFile = File(...)):
    contents = await file.read()
    mime = file.content_type or "image/jpeg"
    b64 = base64.b64encode(contents).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": (
                    "Baca dan transkripsikan resep dokter ini. Kembalikan JSON: "
                    '{"patient_name":"","doctor_name":"",'
                    '"medications":[{"name":"","dosage":"","frequency":"","duration":""}],'
                    '"notes":""}. Pertahankan nama pasien, dokter, obat, dosis, dan teks asli yang '
                    "terbaca. Tulis frequency, duration, dan notes dalam Bahasa Indonesia. Jangan "
                    "menebak tulisan yang tidak terbaca; gunakan nilai kosong. Hanya kembalikan JSON valid."
                )},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }
    ]
    result = await chat_completion(messages)
    try:
        return parse_json_response(result)
    except Exception:
        return {"raw_text": result, "medications": []}


class InteractionRequest(BaseModel):
    drug_names: list[str]


@app.post("/api/ai/interactions")
async def check_interactions(req: InteractionRequest):
    if len(req.drug_names) < 2:
        return {"error": "Minimal 2 obat untuk cek interaksi"}
    drugs_str = ", ".join(req.drug_names)
    messages = [
        {"role": "system", "content": (
            "Anda adalah pakar farmasi. Seluruh penjelasan, rekomendasi, dan ringkasan "
            "wajib menggunakan Bahasa Indonesia yang mudah dipahami. Selalu kembalikan JSON valid."
        )},
        {"role": "user", "content": (
            f"Periksa interaksi antara obat berikut: {drugs_str}. Kembalikan JSON: "
            '{"interactions":[{"drugs":["A","B"],"severity":"high/medium/low",'
            '"description":"penjelasan dalam Bahasa Indonesia",'
            '"recommendation":"tindakan yang disarankan dalam Bahasa Indonesia"}],'
            '"overall_safety":"safe/caution/unsafe",'
            '"summary":"ringkasan singkat dalam Bahasa Indonesia"}. '
            "Jangan terjemahkan nama obat atau nilai severity dan overall_safety."
        )},
    ]
    result = await chat_completion(messages)
    try:
        return parse_json_response(result)
    except Exception:
        return {"summary": result, "interactions": [], "overall_safety": "unknown"}


@app.get("/api/drugs")
def list_drugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
):
    from sqlalchemy import create_engine, or_
    from sqlalchemy.orm import Session, DeclarativeBase

    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pharmaidb")
    engine = create_engine(DATABASE_URL)

    class Base(DeclarativeBase):
        pass

    from sqlalchemy import JSON, Column, Date, Integer, String, Text, DateTime

    class Drug(Base):
        __tablename__ = "drugs"
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        generic_name = Column(String(255))
        category = Column(String(100))
        description = Column(Text)
        dosage_form = Column(String(500))
        indication = Column(Text)
        benefit = Column(Text)
        dosage = Column(Text)
        usage_time = Column(JSON)
        frequency = Column(String(100))
        manufacturer = Column(String(255))
        image_url = Column(String(500))
        active_ingredients = Column(JSON)
        registration_number = Column(String(100))
        registration_status = Column(String(30))
        registration_expires_at = Column(Date)
        regulatory_source_url = Column(String(1000))
        regulatory_checked_at = Column(DateTime)
        regulatory_notes = Column(Text)
        source_product_id = Column(String(100))
        source_application_id = Column(String(50))
        created_at = Column(DateTime)
        updated_at = Column(DateTime)

    with Session(engine) as db:
        query = db.query(Drug)
        if search:
            query = query.filter(or_(Drug.name.ilike(f"%{search}%"), Drug.generic_name.ilike(f"%{search}%")))
        drugs = query.offset(skip).limit(limit).all()
        return [
            {
                "id": d.id, "name": d.name, "generic_name": d.generic_name,
                "category": d.category, "description": d.description,
                "dosage_form": d.dosage_form, "manufacturer": d.manufacturer,
                "indication": d.indication, "benefit": d.benefit, "dosage": d.dosage,
                "usage_time": d.usage_time or [], "frequency": d.frequency,
                "image_url": d.image_url, "active_ingredients": d.active_ingredients or [],
                "registration_number": d.registration_number,
                "registration_status": d.registration_status or "unverified",
                "registration_expires_at": d.registration_expires_at,
                "regulatory_source_url": d.regulatory_source_url,
                "regulatory_checked_at": d.regulatory_checked_at,
                "regulatory_notes": d.regulatory_notes,
                "source_product_id": d.source_product_id,
                "source_application_id": d.source_application_id,
            }
            for d in drugs
        ]


@app.get("/api/drugs/count")
def count_drugs(search: str | None = None):
    from sqlalchemy import create_engine, text

    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pharmaidb")
    engine = create_engine(database_url)
    with engine.connect() as connection:
        if search:
            total = connection.execute(
                text("SELECT COUNT(*) FROM drugs WHERE name ILIKE :search OR generic_name ILIKE :search"),
                {"search": f"%{search}%"},
            ).scalar_one()
        else:
            total = connection.execute(text("SELECT COUNT(*) FROM drugs")).scalar_one()
    return {"total": total}


@app.get("/api/drugs/{drug_id}")
def get_drug(drug_id: int):
    from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, create_engine
    from sqlalchemy.orm import DeclarativeBase, Session

    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pharmaidb")
    engine = create_engine(database_url)

    class Base(DeclarativeBase):
        pass

    class Drug(Base):
        __tablename__ = "drugs"
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        generic_name = Column(String(255))
        category = Column(String(100))
        description = Column(Text)
        dosage_form = Column(String(500))
        indication = Column(Text)
        benefit = Column(Text)
        dosage = Column(Text)
        usage_time = Column(JSON)
        frequency = Column(String(100))
        manufacturer = Column(String(255))
        image_url = Column(String(500))
        active_ingredients = Column(JSON)
        registration_number = Column(String(100))
        registration_status = Column(String(30))
        registration_expires_at = Column(Date)
        regulatory_source_url = Column(String(1000))
        regulatory_checked_at = Column(DateTime)
        regulatory_notes = Column(Text)
        source_product_id = Column(String(100))
        source_application_id = Column(String(50))
        created_at = Column(DateTime)
        updated_at = Column(DateTime)

    with Session(engine) as db:
        drug = db.query(Drug).filter(Drug.id == drug_id).first()
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return {
            "id": drug.id, "name": drug.name, "generic_name": drug.generic_name,
            "category": drug.category, "description": drug.description,
            "dosage_form": drug.dosage_form, "manufacturer": drug.manufacturer,
            "indication": drug.indication, "benefit": drug.benefit, "dosage": drug.dosage,
            "usage_time": drug.usage_time or [], "frequency": drug.frequency,
            "image_url": drug.image_url, "active_ingredients": drug.active_ingredients or [],
            "registration_number": drug.registration_number,
            "registration_status": drug.registration_status or "unverified",
            "registration_expires_at": drug.registration_expires_at,
            "regulatory_source_url": drug.regulatory_source_url,
            "regulatory_checked_at": drug.regulatory_checked_at,
            "regulatory_notes": drug.regulatory_notes,
            "source_product_id": drug.source_product_id,
            "source_application_id": drug.source_application_id,
        }


class AnalyzeRequest(BaseModel):
    drug_id: int


@app.post("/api/ai/analyze-drug")
async def analyze_drug_endpoint(req: AnalyzeRequest):
    from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, create_engine
    from sqlalchemy.orm import DeclarativeBase, Session

    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pharmaidb")
    engine = create_engine(database_url)

    class Base(DeclarativeBase):
        pass

    class Drug(Base):
        __tablename__ = "drugs"
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        generic_name = Column(String(255))
        category = Column(String(100))
        description = Column(Text)
        dosage_form = Column(String(500))
        indication = Column(Text)
        benefit = Column(Text)
        dosage = Column(Text)
        usage_time = Column(JSON)
        frequency = Column(String(100))
        manufacturer = Column(String(255))
        image_url = Column(String(500))
        active_ingredients = Column(JSON)
        registration_number = Column(String(100))
        registration_status = Column(String(30))
        registration_expires_at = Column(Date)
        regulatory_source_url = Column(String(1000))
        regulatory_checked_at = Column(DateTime)
        regulatory_notes = Column(Text)
        source_product_id = Column(String(100))
        source_application_id = Column(String(50))
        created_at = Column(DateTime)
        updated_at = Column(DateTime)

    with Session(engine) as db:
        drug = db.query(Drug).filter(Drug.id == req.drug_id).first()
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        drug_data = {
            "name": drug.name,
            "generic_name": drug.generic_name,
            "category": drug.category,
            "description": drug.description,
            "dosage_form": drug.dosage_form,
            "manufacturer": drug.manufacturer,
            "indication": drug.indication,
            "benefit": drug.benefit,
            "dosage": drug.dosage,
            "usage_time": drug.usage_time or [],
            "frequency": drug.frequency,
            "active_ingredients": drug.active_ingredients or [],
        }

    has_existing = any([
        drug_data["indication"], drug_data["benefit"],
        drug_data["dosage"], drug_data["usage_time"], drug_data["frequency"],
    ])

    if has_existing:
        prompt = (
            f"Berikut adalah data obat yang sudah ada:\n"
            f"Nama: {drug_data['name']}\n"
            f"Nama generik: {drug_data['generic_name'] or ''}\n"
            f"Kategori: {drug_data['category'] or ''}\n"
            f"Bentuk sediaan: {drug_data['dosage_form'] or ''}\n"
            f"PRODUSEN: {drug_data['manufacturer'] or ''}\n"
            f"Deskripsi: {drug_data['description'] or ''}\n"
            f"Zat aktif: {', '.join(drug_data['active_ingredients']) if drug_data['active_ingredients'] else 'N/A'}\n"
            f"Indikasi saat ini: {drug_data['indication'] or 'kosong'}\n"
            f"Manfaat saat ini: {drug_data['benefit'] or 'kosong'}\n"
            f"Dosis saat ini: {drug_data['dosage'] or 'kosong'}\n"
            f"Waktu pakai saat ini: {', '.join(drug_data['usage_time']) if drug_data['usage_time'] else 'kosong'}\n"
            f"Frekuensi saat ini: {drug_data['frequency'] or 'kosong'}\n\n"
            f"Berdasarkan data di atas, berikan analisis lengkap penggunaan yang aman dan "
            f"sesuai petunjuk. Jika ada field yang kosong, lengkapi berdasarkan pengetahuan "
            f"farmakologi obat tersebut. Jika ada field yang sudah terisi, verifikasi dan "
            f"pertahankan kesesuaiannya. Kembalikan JSON valid:\n"
            f'{{"indication": "untuk apa obat ini digunakan", '
            f'"benefit": "manfaat penggunaan", '
            f'"dosage": "dosis yang disarankan", '
            f'"usage_time": ["pagi", "siang", "sore", "malam"], '
            f'"frequency": "frekuensi penggunaan", '
            f'"confidence": 0.0-1.0}}'
        )
    else:
        prompt = (
            f"Berikan analisis penggunaan yang aman dan sesuai petunjuk untuk obat berikut:\n"
            f"Nama: {drug_data['name']}\n"
            f"Nama generik: {drug_data['generic_name'] or ''}\n"
            f"Kategori: {drug_data['category'] or ''}\n"
            f"Bentuk sediaan: {drug_data['dosage_form'] or ''}\n"
            f"PRODUSEN: {drug_data['manufacturer'] or ''}\n"
            f"Deskripsi: {drug_data['description'] or ''}\n"
            f"Zat aktif: {', '.join(drug_data['active_ingredients']) if drug_data['active_ingredients'] else 'N/A'}\n\n"
            f"Kembalikan JSON valid dengan field:\n"
            f'{{"indication": "untuk apa obat ini digunakan", '
            f'"benefit": "manfaat penggunaan", '
            f'"dosage": "dosis yang disarankan", '
            f'"usage_time": ["pagi", "siang", "sore", "malam"], '
            f'"frequency": "frekuensi penggunaan", '
            f'"confidence": 0.0-1.0}}\n'
            f"Jika informasi tidak cukup, gunakan nilai kosong dan confidence rendah. "
            f"Semua teks dalam Bahasa Indonesia."
        )

    messages = [
        {"role": "system", "content": (
            "Anda adalah pakar farmasi Indonesia. Berikan analisis penggunaan obat "
            "yang akurat, aman, dan mudah dipahami dalam Bahasa Indonesia. "
            "Selalu kembalikan JSON valid."
        )},
        {"role": "user", "content": prompt},
    ]
    result = await chat_completion(messages)
    import json

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {
            "indication": "",
            "benefit": "",
            "dosage": "",
            "usage_time": [],
            "frequency": "",
            "confidence": 0.0,
            "raw_response": result,
        }
