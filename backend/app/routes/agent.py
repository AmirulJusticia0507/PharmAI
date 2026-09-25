from fastapi import APIRouter
from pydantic import BaseModel
from ..autonomous_agent import (
    get_state,
    is_running,
    run_batch,
    get_unanalyzed_count,
    get_analyzed_count,
)

router = APIRouter(prefix="/agent", tags=["agent"])


class RunRequest(BaseModel):
    batch_size: int | None = 5


@router.get("/status")
async def agent_status():
    state = get_state()
    return {
        "running": state["running"],
        "processed": state["processed"],
        "total": state["total"],
        "failed": state["failed"],
        "current_drug": state["current_drug"],
        "started_at": state["started_at"],
        "last_run": state["last_run"],
        "unanalyzed_count": get_unanalyzed_count(),
        "analyzed_count": get_analyzed_count(),
    }


@router.post("/run")
async def agent_run(req: RunRequest):
    result = await run_batch(req.batch_size)
    return result


@router.get("/tasks")
async def agent_tasks():
    state = get_state()
    return {
        "running": state["running"],
        "tasks": state["tasks"],
        "processed": state["processed"],
        "failed": state["failed"],
        "total": state["total"],
        "last_run": state["last_run"],
    }


@router.get("/tasks/clear")
async def agent_clear_tasks():
    state = get_state()
    state["tasks"] = []
    from ..autonomous_agent import _save_state
    _save_state()
    return {"status": "cleared", "tasks": []}
