from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..ai_service import analyze_pill_image, ocr_prescription, check_drug_interactions, analyze_drug
from ..database import get_db
from ..models import Drug

router = APIRouter(prefix="/ai", tags=["ai"])


class InteractionRequest(BaseModel):
    drug_names: list[str]


class DrugAnalyzeRequest(BaseModel):
    drug_id: int


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
