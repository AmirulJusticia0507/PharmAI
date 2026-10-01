from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..ai_service import analyze_pill_image, ocr_prescription, check_drug_interactions, analyze_drug, generate_drug_visual, assess_symptoms
from ..database import get_db
from ..models import Drug

router = APIRouter(prefix="/ai", tags=["ai"])


class InteractionRequest(BaseModel):
    drug_names: list[str]


class DrugAnalyzeRequest(BaseModel):
    drug_id: int


class DrugVisualRequest(BaseModel):
    drug_id: int
    use_premium: bool = False


class SymptomRequest(BaseModel):
    complaint: str = Field(min_length=10, max_length=3000)
    age: int | None = Field(default=None, ge=0, le=120)
    sex: str | None = Field(default=None, max_length=30)
    duration: str | None = Field(default=None, max_length=200)
    existing_conditions: str | None = Field(default=None, max_length=1000)
    current_medicines: str | None = Field(default=None, max_length=1000)
    allergies: str | None = Field(default=None, max_length=500)
    pregnancy_status: str | None = Field(default=None, max_length=100)


@router.post("/scan-pill")
async def scan_pill(file: UploadFile = File(...)):
    contents = await file.read()
    mime = file.content_type or "image/jpeg"
    result = await analyze_pill_image(contents, mime)
    return result


@router.post("/ocr-prescription")
async def ocr_prescription(file: UploadFile = File(...)):
    contents = await file.read()
    mime = file.content_type or "image/jpeg"
    result = await ocr_prescription(contents, mime)
    return result


@router.post("/interactions")
async def check_interactions(req: InteractionRequest):
    if len(req.drug_names) < 2:
        return {"error": "Minimal 2 obat untuk cek interaksi"}
    result = await check_drug_interactions(req.drug_names)
    return result


@router.post("/symptom-assessment")
async def symptom_assessment(req: SymptomRequest):
    try:
        return await assess_symptoms(req.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/analyze-drug")
async def analyze_endpoint(req: DrugAnalyzeRequest, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == req.drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
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
    result = await analyze_drug(drug_data)
    return result


@router.post("/generate-drug-image")
async def generate_drug_image(req: DrugVisualRequest, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == req.drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Obat tidak ditemukan")
    drug_data = {
        "name": drug.name,
        "generic_name": drug.generic_name,
        "dosage_form": drug.dosage_form,
        "manufacturer": drug.manufacturer,
        "description": drug.description,
        "active_ingredients": drug.active_ingredients or [],
        "dosage": drug.dosage or "",
        "color": getattr(drug, "color", "") or "",
        "shape": getattr(drug, "shape", "") or "",
        "imprint": getattr(drug, "imprint", "") or "",
    }
    try:
        result = await generate_drug_visual(drug_data, use_premium=req.use_premium)
        drug.image_url = result["image_url"]
        db.commit()
        return result
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
