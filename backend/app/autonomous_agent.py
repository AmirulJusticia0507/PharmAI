import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import or_, func
from .ai_service import analyze_drug
from .database import SessionLocal
from .models import Drug

_STATE_FILE = Path(__file__).resolve().parent.parent / ".agent_state.json"

_BATCH_SIZE = 5
_DELAY_BETWEEN_DRUGS = 0.5

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


def _load_state() -> dict:
    global _agent_state
    if _STATE_FILE.exists():
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as f:
                loaded = json.loads(f.read())
                _agent_state.update(loaded)
        except Exception:
            pass
    return _agent_state


def _save_state() -> None:
    try:
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(_agent_state, f, indent=2, default=str)
    except Exception:
        pass


def get_state() -> dict:
    _load_state()
    return _agent_state


def is_running() -> bool:
    _load_state()
    return _agent_state["running"]


_unanalyzed_filter = or_(
    Drug.indication.is_(None),
    Drug.benefit.is_(None),
    Drug.dosage.is_(None),
    Drug.usage_time.is_(None),
    Drug.frequency.is_(None),
)

_analyzed_filter = or_(
    Drug.indication.is_not(None),
    Drug.benefit.is_not(None),
    Drug.dosage.is_not(None),
    Drug.usage_time.is_not(None),
    Drug.frequency.is_not(None),
)


async def run_batch(batch_size: int = _BATCH_SIZE) -> dict:
    _load_state()

    if _agent_state["running"]:
        return {"status": "already_running", "message": "Agent sudah berjalan"}

    db = SessionLocal()
    try:
        unanalyzed = db.query(Drug).filter(_unanalyzed_filter).limit(batch_size).all()

        if not unanalyzed:
            _agent_state["last_run"] = datetime.now(timezone.utc).isoformat()
            _save_state()
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
        _save_state()

        results = []

        for drug in unanalyzed:
            try:
                _agent_state["current_drug"] = {
                    "id": drug.id,
                    "name": drug.name,
                }
                _save_state()

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

                analysis = await analyze_drug(drug_data)

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

            _agent_state["tasks"] = results
            _save_state()

            await asyncio.sleep(_DELAY_BETWEEN_DRUGS)

        _agent_state["running"] = False
        _agent_state["current_drug"] = None
        _agent_state["last_run"] = datetime.now(timezone.utc).isoformat()
        _save_state()

        return {
            "status": "completed",
            "batch_size": batch_size,
            "processed": _agent_state["processed"],
            "failed": _agent_state["failed"],
            "results": results,
        }

    finally:
        db.close()


def get_unanalyzed_count() -> int:
    db = SessionLocal()
    try:
        return db.query(Drug).filter(_unanalyzed_filter).count()
    finally:
        db.close()


def get_analyzed_count() -> int:
    db = SessionLocal()
    try:
        return db.query(Drug).filter(_analyzed_filter).count()
    finally:
        db.close()
