from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from ..ai_service import analyze_pill_image, ocr_prescription, check_drug_interactions

router = APIRouter(prefix="/ai", tags=["ai"])


class InteractionRequest(BaseModel):
    drug_names: list[str]


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
