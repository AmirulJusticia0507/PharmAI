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
from datetime import datetime, timezone

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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
PREMIUM_IMAGE_MODEL = os.getenv("PREMIUM_IMAGE_MODEL", "dall-e-3")
STANDARD_IMAGE_MODEL = os.getenv("STANDARD_IMAGE_MODEL", "dall-e-2")


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


async def _analyze_drug_inline(drug_data: dict) -> dict:
    has_existing_data = any([
        drug_data.get("indication"),
        drug_data.get("benefit"),
        drug_data.get("dosage"),
        drug_data.get("usage_time"),
        drug_data.get("frequency"),
    ])

    name = drug_data.get("name") or ""
    generic_name = drug_data.get("generic_name") or ""
    category = drug_data.get("category") or ""
    description = drug_data.get("description") or ""
    dosage_form = drug_data.get("dosage_form") or ""
    manufacturer = drug_data.get("manufacturer") or ""
    active_ingredients = drug_data.get("active_ingredients") or []
    indication = drug_data.get("indication") or ""
    benefit = drug_data.get("benefit") or ""
    dosage = drug_data.get("dosage") or ""
    usage_time = drug_data.get("usage_time") or []
    frequency = drug_data.get("frequency") or ""

    if has_existing_data:
        prompt = (
            f"Berikut adalah data obat yang sudah ada:\n"
            f"Nama: {name}\n"
            f"Nama generik: {generic_name}\n"
            f"Kategori: {category}\n"
            f"Bentuk sediaan: {dosage_form}\n"
            f"PRODUSEN: {manufacturer}\n"
            f"Deskripsi: {description}\n"
            f"Zat aktif: {', '.join(active_ingredients) if active_ingredients else 'N/A'}\n"
            f"Indikasi saat ini: {indication or 'kosong'}\n"
            f"Manfaat saat ini: {benefit or 'kosong'}\n"
            f"Dosis saat ini: {dosage or 'kosong'}\n"
            f"Waktu pakai saat ini: {', '.join(usage_time) if usage_time else 'kosong'}\n"
            f"Frekuensi saat ini: {frequency or 'kosong'}\n\n"
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
            f"Nama: {name}\n"
            f"Nama generik: {generic_name}\n"
            f"Kategori: {category}\n"
            f"Bentuk sediaan: {dosage_form}\n"
            f"PRODUSEN: {manufacturer}\n"
            f"Deskripsi: {description}\n"
            f"Zat aktif: {', '.join(active_ingredients) if active_ingredients else 'N/A'}\n\n"
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
        {
            "role": "system",
            "content": (
                "Anda adalah pakar farmasi Indonesia. Berikan analisis penggunaan obat "
                "yang akurat, aman, dan mudah dipahami dalam Bahasa Indonesia. "
                "Selalu kembalikan JSON valid."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    result = await chat_completion(messages)

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


_agent_state: dict = {
    "running": False,
    "processed": 0,
    "total": 0,
    "failed": 0,
    "current_drug": None,
    "started_at": None,
    "last_run": None,
    "tasks": [],
}


class AgentRunRequest(BaseModel):
    batch_size: int | None = 5


@app.get("/api/agent/status")
def agent_status():
    from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, create_engine, or_
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
        created_at = Column(DateTime(timezone=True))
        updated_at = Column(DateTime(timezone=True))

    unanalyzed_filter = or_(
        Drug.indication.is_(None),
        Drug.benefit.is_(None),
        Drug.dosage.is_(None),
        Drug.usage_time.is_(None),
        Drug.frequency.is_(None),
    )

    with Session(engine) as db:
        unanalyzed_count = db.query(Drug).filter(unanalyzed_filter).count()
        analyzed_count = db.query(Drug).filter(
            or_(
                Drug.indication.is_not(None),
                Drug.benefit.is_not(None),
                Drug.dosage.is_not(None),
            )
        ).count()

    _agent_state.update({
        "unanalyzed_count": unanalyzed_count,
        "analyzed_count": analyzed_count,
    })
    return _agent_state


@app.post("/api/agent/run")
async def agent_run(req: AgentRunRequest):
    from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, create_engine, or_
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
        created_at = Column(DateTime(timezone=True))
        updated_at = Column(DateTime(timezone=True))

    unanalyzed_filter = or_(
        Drug.indication.is_(None),
        Drug.benefit.is_(None),
        Drug.dosage.is_(None),
        Drug.usage_time.is_(None),
        Drug.frequency.is_(None),
    )

    if _agent_state["running"]:
        return {"status": "already_running", "message": "Agent sudah berjalan"}

    results = []

    with Session(engine) as db:
        unanalyzed = db.query(Drug).filter(unanalyzed_filter).limit(req.batch_size or 5).all()

        if not unanalyzed:
            return {
                "status": "completed",
                "message": "Semua obat sudah dianalisis",
                "processed": 0,
            }

        _agent_state["running"] = True
        _agent_state["total"] = len(unanalyzed)
        _agent_state["processed"] = 0
        _agent_state["failed"] = 0
        _agent_state["started_at"] = datetime.now(timezone.utc).isoformat()
        _agent_state["current_drug"] = None

        for drug in unanalyzed:
            try:
                _agent_state["current_drug"] = {"id": drug.id, "name": drug.name}

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

                analysis = await _analyze_drug_inline(drug_data)

                drug.indication = analysis.get("indication") or drug.indication
                drug.benefit = analysis.get("benefit") or drug.benefit
                drug.dosage = analysis.get("dosage") or drug.dosage
                if analysis.get("usage_time") and len(analysis["usage_time"]) > 0:
                    drug.usage_time = analysis["usage_time"]
                if analysis.get("frequency"):
                    drug.frequency = analysis["frequency"]

                db.commit()
                _agent_state["processed"] += 1
                results.append({
                    "drug_id": drug.id,
                    "name": drug.name,
                    "status": "success",
                    "confidence": analysis.get("confidence", 0),
                })

            except Exception as e:
                db.rollback()
                _agent_state["failed"] += 1
                results.append({
                    "drug_id": drug.id,
                    "name": drug.name,
                    "status": "failed",
                    "error": str(e),
                })

    _agent_state["running"] = False
    _agent_state["current_drug"] = None
    _agent_state["last_run"] = datetime.now(timezone.utc).isoformat()
    _agent_state["tasks"] = results
    return {
        "status": "completed",
        "batch_size": req.batch_size or 5,
        "processed": _agent_state["processed"],
        "failed": _agent_state["failed"],
        "results": results,
    }


@app.get("/api/agent/tasks")
def agent_tasks():
    return {
        "running": _agent_state["running"],
        "tasks": _agent_state["tasks"],
        "processed": _agent_state["processed"],
        "failed": _agent_state["failed"],
        "total": _agent_state["total"],
        "last_run": _agent_state["last_run"],
    }


@app.get("/api/agent/tasks/clear")
def agent_clear_tasks():
    _agent_state["tasks"] = []
    return {"status": "cleared", "tasks": []}


class DrugVisualRequest(BaseModel):
    drug_id: int
    use_premium: bool = False


@app.post("/api/ai/generate-drug-image")
async def generate_drug_image(req: DrugVisualRequest):
    from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text, create_engine
    from sqlalchemy.orm import DeclarativeBase, Session

    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY belum dikonfigurasi untuk generasi gambar",
        )

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
        manufacturer = Column(String(255))
        dosage = Column(Text)
        active_ingredients = Column(JSON)
        color = Column(String(100))
        shape = Column(String(100))
        imprint = Column(String(255))

    with Session(engine) as db:
        drug = db.query(Drug).filter(Drug.id == req.drug_id).first()
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        drug_data = {
            "name": drug.name,
            "generic_name": drug.generic_name or "",
            "dosage_form": drug.dosage_form or "",
            "manufacturer": drug.manufacturer or "",
            "description": drug.description or "",
            "active_ingredients": drug.active_ingredients or [],
            "dosage": drug.dosage or "",
            "color": drug.color or "",
            "shape": drug.shape or "",
            "imprint": drug.imprint or "",
        }

    prompt = (
        f"Gambar realistis dari obat atau kemasannya. "
        f"Nama obat: {drug_data['name']}. Nama generik: {drug_data['generic_name']}. "
        f"Bentuk sediaan: {drug_data['dosage_form']}. "
        f"Warna: {drug_data['color'] or 'tidak ditentukan'}. "
        f"Bentuk: {drug_data['shape'] or 'tidak ditentukan'}. "
        f"Imprint/atau kode pada permukaan: {drug_data['imprint'] or 'tidak ada'}. "
        f"Dosis: {drug_data['dosage'] or 'tidak ditentukan'}. "
        f"PRODUSEN: {drug_data['manufacturer'] or 'tidak ditentukan'}. "
        f"Zat aktif: {', '.join(drug_data['active_ingredients']) if drug_data['active_ingredients'] else 'N/A'}. "
        f"Deskripsi: {drug_data['description'] or 'tidak tersedia'}. "
        f"Gambarkan permukaan obat (tablet, kapsul, kaplet) secara detail termasuk warna, "
        f"bentuk, tekstur, dan imprint jika ada. Jika obat cair, gambarkan butir/ Botol "
        f"kemasannya. Fotografi realistis dengan pencahayaan studio yang baik, latar belakang "
        f"putih bersih. Jangan termasuk teks, logo, atau watermark."
    )

    model = PREMIUM_IMAGE_MODEL if req.use_premium else STANDARD_IMAGE_MODEL

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL.rstrip('/')}/images/generations",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
            },
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
        data = resp.json()

    image_url = data.get("data", [{}])[0].get("url", "")
    revised_prompt = data.get("data", [{}])[0].get("revised_prompt", "")

    return {
        "image_url": image_url,
        "revised_prompt": revised_prompt,
        "model": model,
        "premium": req.use_premium,
    }
