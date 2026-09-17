from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import drugs, ai

app = FastAPI(
    title="PharmAI API",
    description="API untuk analisis obat berbasis AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drugs.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "PharmAI API is running"}


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
