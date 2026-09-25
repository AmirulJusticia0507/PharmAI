from pydantic import BaseModel, Field
from datetime import date, datetime


class DrugBase(BaseModel):
    name: str
    generic_name: str | None = None
    category: str | None = None
    description: str | None = None
    dosage_form: str | None = None
    indication: str | None = None
    benefit: str | None = None
    dosage: str | None = None
    usage_time: list[str] | None = None
    frequency: str | None = None
    manufacturer: str | None = None
    image_url: str | None = None
    active_ingredients: list[str] = Field(default_factory=list)
    registration_number: str | None = None
    registration_status: str = "unverified"
    registration_expires_at: date | None = None
    regulatory_source_url: str | None = None
    regulatory_checked_at: datetime | None = None
    regulatory_notes: str | None = None
    source_product_id: str | None = None
    source_application_id: str | None = None


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
