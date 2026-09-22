from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Drug
from ..schemas import DrugCreate, DrugResponse

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("/", response_model=list[DrugResponse])
def list_drugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Drug)
    if search:
        query = query.filter(
            or_(
                Drug.name.ilike(f"%{search}%"),
                Drug.generic_name.ilike(f"%{search}%"),
            )
        )
    if category:
        query = query.filter(Drug.category == category)
    return query.offset(skip).limit(limit).all()


@router.get("/count")
def count_drugs(db: Session = Depends(get_db)):
    return {"total": db.query(Drug).count()}


@router.get("/{drug_id}", response_model=DrugResponse)
def get_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug


@router.post("/", response_model=DrugResponse, status_code=201)
def create_drug(drug_in: DrugCreate, db: Session = Depends(get_db)):
    drug = Drug(**drug_in.model_dump())
    db.add(drug)
    db.commit()
    db.refresh(drug)
    return drug


@router.put("/{drug_id}", response_model=DrugResponse)
def update_drug(drug_id: int, drug_in: DrugCreate, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    for field, value in drug_in.model_dump(exclude_unset=True).items():
        setattr(drug, field, value)
    db.commit()
    db.refresh(drug)
    return drug


@router.delete("/{drug_id}", status_code=204)
def delete_drug(drug_id: int, db: Session = Depends(get_db)):
    drug = db.query(Drug).filter(Drug.id == drug_id).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    db.delete(drug)
    db.commit()
