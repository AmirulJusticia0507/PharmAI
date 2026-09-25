from sqlalchemy import JSON, Column, Date, Integer, String, Text, DateTime, func
from .database import Base


class Drug(Base):
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    generic_name = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    dosage_form = Column(String(500), nullable=True)
    indication = Column(Text, nullable=True)
    benefit = Column(Text, nullable=True)
    dosage = Column(Text, nullable=True)
    usage_time = Column(JSON, nullable=False, default=list)
    frequency = Column(String(100), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    active_ingredients = Column(JSON, nullable=False, default=list)
    registration_number = Column(String(100), nullable=True, index=True)
    registration_status = Column(String(30), nullable=False, default="unverified")
    registration_expires_at = Column(Date, nullable=True)
    regulatory_source_url = Column(String(1000), nullable=True)
    regulatory_checked_at = Column(DateTime(timezone=True), nullable=True)
    regulatory_notes = Column(Text, nullable=True)
    source_product_id = Column(String(100), nullable=True)
    source_application_id = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, index=True)
    drug_a_id = Column(Integer, nullable=False)
    drug_b_id = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
