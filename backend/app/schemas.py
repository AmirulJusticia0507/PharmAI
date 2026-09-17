from pydantic import BaseModel
from datetime import datetime


class DrugBase(BaseModel):
    name: str
    generic_name: str | None = None
    category: str | None = None
    description: str | None = None
    dosage_form: str | None = None
    manufacturer: str | None = None
    image_url: str | None = None


class DrugCreate(DrugBase):
    pass


class DrugResponse(DrugBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InteractionResponse(BaseModel):
    id: int
    drug_a_id: int
    drug_b_id: int
    severity: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    message: str
