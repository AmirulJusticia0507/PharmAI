from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import base64
import os
import json

app = FastAPI(title="PharmAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")
OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "https://omniroute.online/v1")


async def chat_completion(messages: list[dict], model: str = "auto") -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OMNIROUTE_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OMNIROUTE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages, "max_tokens": 1024},
        )
        resp.raise_for_status()
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
                    "Analyze this pill/capsule image. Return JSON: "
                    '{"name":"drug name","dosage":"dosage","category":"category",'
                    '"description":"brief description","confidence":0.0-1.0}. Only valid JSON.'
                )},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }
    ]
    result = await chat_completion(messages)
    try:
        return parse_json_response(result)
    except Exception:
        return {"name": "Unknown", "description": result, "confidence": 0.0}


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
                    "Read this handwritten prescription. Return JSON: "
                    '{"patient_name":"","doctor_name":"",'
                    '"medications":[{"name":"","dosage":"","frequency":"","duration":""}],'
                    '"notes":""}. Only valid JSON.'
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
        {"role": "system", "content": "You are a pharmaceutical expert. Always return valid JSON."},
        {"role": "user", "content": (
            f"Check interactions between: {drugs_str}. Return JSON: "
            '{"interactions":[{"drugs":["A","B"],"severity":"high/medium/low",'
            '"description":"explanation","recommendation":"what to do"}],'
            '"overall_safety":"safe/caution/unsafe","summary":"brief summary"}.'
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

    from sqlalchemy import Column, Integer, String, Text, DateTime, func

    class Drug(Base):
        __tablename__ = "drugs"
        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        generic_name = Column(String(255))
        category = Column(String(100))
        description = Column(Text)
        dosage_form = Column(String(100))
        manufacturer = Column(String(255))
        image_url = Column(String(500))
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
                "image_url": d.image_url,
            }
            for d in drugs
        ]
